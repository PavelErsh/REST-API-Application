from pydantic import BaseModel, Field
from typing import List, Optional


class PhoneNumberBase(BaseModel):
    number: str


class PhoneNumberCreate(PhoneNumberBase):
    pass


class PhoneNumber(PhoneNumberBase):
    id: int
    organization_id: int

    class Config:
        from_attributes = True


class BuildingBase(BaseModel):
    address: str
    latitude: float = Field(
        ..., ge=-90, le=90, description="Latitude must be between -90 and 90"
    )
    longitude: float = Field(
        ..., ge=-180, le=180, description="Longitude must be between -180 and 180"
    )


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    id: int

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    level: int = Field(default=1, ge=1, le=3, description="Activity level (1-3)")


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True


class ActivityTree(Activity):
    children: List["ActivityTree"] = []

    class Config:
        from_attributes = True


# Organization Schemas
class OrganizationBase(BaseModel):
    name: str
    building_id: int


class OrganizationCreate(OrganizationBase):
    phone_numbers: List[str] = []
    activity_ids: List[int] = []


class Organization(OrganizationBase):
    id: int
    phone_numbers: List[PhoneNumber] = []
    activities: List[Activity] = []

    class Config:
        from_attributes = True


class OrganizationDetail(Organization):
    building: Building

    class Config:
        from_attributes = True


class LocationSearch(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius: Optional[float] = Field(
        None, gt=0, description="Search radius in kilometers"
    )
    min_latitude: Optional[float] = Field(None, ge=-90, le=90)
    max_latitude: Optional[float] = Field(None, ge=-90, le=90)
    min_longitude: Optional[float] = Field(None, ge=-180, le=180)
    max_longitude: Optional[float] = Field(None, ge=-180, le=180)


ActivityTree.model_rebuild()
