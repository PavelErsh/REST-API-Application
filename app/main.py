from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import math
from app.database import get_db
from app import models, schemas
from app.auth import verify_api_key

app = FastAPI(
    title="Organizations Directory API",
    description="REST API для справочника Организаций, Зданий и Деятельности",
    version="1.0.0",
)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    R = 6371  # Radius of the Earth in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def get_all_child_activity_ids(db: Session, activity_id: int) -> List[int]:

    activity_ids = [activity_id]

    def get_children(parent_id: int):
        children = (
            db.query(models.Activity)
            .filter(models.Activity.parent_id == parent_id)
            .all()
        )
        for child in children:
            activity_ids.append(child.id)
            get_children(child.id)

    get_children(activity_id)
    return activity_ids


@app.get("/", tags=["Root"])
async def root():

    return {
        "message": "Organizations Directory API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get(
    "/organizations/",
    response_model=List[schemas.OrganizationDetail],
    tags=["Organizations"],
)
async def list_organizations(
    db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):

    organizations = db.query(models.Organization).all()
    return organizations


@app.get(
    "/organizations/{organization_id}",
    response_model=schemas.OrganizationDetail,
    tags=["Organizations"],
)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):

    organization = (
        db.query(models.Organization)
        .filter(models.Organization.id == organization_id)
        .first()
    )
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@app.get(
    "/organizations/building/{building_id}",
    response_model=List[schemas.OrganizationDetail],
    tags=["Organizations"],
)
async def get_organizations_by_building(
    building_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):

    building = (
        db.query(models.Building).filter(models.Building.id == building_id).first()
    )
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    organizations = (
        db.query(models.Organization)
        .filter(models.Organization.building_id == building_id)
        .all()
    )
    return organizations


@app.get(
    "/organizations/activity/{activity_id}",
    response_model=List[schemas.OrganizationDetail],
    tags=["Organizations"],
)
async def get_organizations_by_activity(
    activity_id: int,
    include_children: bool = Query(
        True, description="Include organizations from child activities"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):

    activity = (
        db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if include_children:

        activity_ids = get_all_child_activity_ids(db, activity_id)

        organizations = (
            db.query(models.Organization)
            .join(models.organization_activity)
            .filter(models.organization_activity.c.activity_id.in_(activity_ids))
            .distinct()
            .all()
        )
    else:

        organizations = (
            db.query(models.Organization)
            .join(models.organization_activity)
            .filter(models.organization_activity.c.activity_id == activity_id)
            .all()
        )

    return organizations


@app.get(
    "/organizations/search/by-name",
    response_model=List[schemas.OrganizationDetail],
    tags=["Organizations"],
)
async def search_organizations_by_name(
    name: str = Query(..., description="Search query for organization name"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):

    organizations = (
        db.query(models.Organization)
        .filter(models.Organization.name.ilike(f"%{name}%"))
        .all()
    )
    return organizations


@app.post(
    "/organizations/search/by-location",
    response_model=List[schemas.OrganizationDetail],
    tags=["Organizations"],
)
async def search_organizations_by_location(
    search: schemas.LocationSearch,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):

    buildings = db.query(models.Building).all()

    matching_building_ids = []

    if search.radius is not None:

        for building in buildings:
            distance = haversine_distance(
                search.latitude, search.longitude, building.latitude, building.longitude
            )
            if distance <= search.radius:
                matching_building_ids.append(building.id)

    elif all(
        [
            search.min_latitude,
            search.max_latitude,
            search.min_longitude,
            search.max_longitude,
        ]
    ):

        for building in buildings:
            if (
                search.min_latitude <= building.latitude <= search.max_latitude
                and search.min_longitude <= building.longitude <= search.max_longitude
            ):
                matching_building_ids.append(building.id)
    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide either 'radius' for circular search or all rectangle boundaries (min_latitude, max_latitude, min_longitude, max_longitude)",
        )

    organizations = (
        db.query(models.Organization)
        .filter(models.Organization.building_id.in_(matching_building_ids))
        .all()
    )

    return organizations


@app.get("/buildings/", response_model=List[schemas.Building], tags=["Buildings"])
async def list_buildings(
    db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):

    buildings = db.query(models.Building).all()
    return buildings


@app.get(
    "/buildings/{building_id}", response_model=schemas.Building, tags=["Buildings"]
)
async def get_building(
    building_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):

    building = (
        db.query(models.Building).filter(models.Building.id == building_id).first()
    )
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@app.get("/activities/", response_model=List[schemas.Activity], tags=["Activities"])
async def list_activities(
    db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):

    activities = db.query(models.Activity).all()
    return activities


@app.get(
    "/activities/tree", response_model=List[schemas.ActivityTree], tags=["Activities"]
)
async def get_activities_tree(
    db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):

    def build_tree(parent_id: Optional[int] = None):
        activities = (
            db.query(models.Activity)
            .filter(models.Activity.parent_id == parent_id)
            .all()
        )
        result = []
        for activity in activities:
            activity_dict = {
                "id": activity.id,
                "name": activity.name,
                "parent_id": activity.parent_id,
                "level": activity.level,
                "children": build_tree(activity.id),
            }
            result.append(activity_dict)
        return result

    return build_tree(None)


@app.get(
    "/activities/{activity_id}", response_model=schemas.Activity, tags=["Activities"]
)
async def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):

    activity = (
        db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
