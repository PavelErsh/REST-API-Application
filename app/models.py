from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Table,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


organization_activity = Table(
    "organization_activity",
    Base.metadata,
    Column(
        "organization_id", Integer, ForeignKey("organizations.id", ondelete="CASCADE")
    ),
    Column("activity_id", Integer, ForeignKey("activities.id", ondelete="CASCADE")),
)


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    organizations = relationship("Organization", back_populates="building")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    parent_id = Column(
        Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=True
    )
    level = Column(Integer, nullable=False, default=1)

    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship(
        "Activity", back_populates="parent", cascade="all, delete-orphan"
    )

    organizations = relationship(
        "Organization", secondary=organization_activity, back_populates="activities"
    )

    __table_args__ = (
        CheckConstraint("level >= 1 AND level <= 3", name="check_activity_level"),
    )


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, nullable=False)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    organization = relationship("Organization", back_populates="phone_numbers")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    building_id = Column(
        Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False
    )

    building = relationship("Building", back_populates="organizations")
    phone_numbers = relationship(
        "PhoneNumber", back_populates="organization", cascade="all, delete-orphan"
    )
    activities = relationship(
        "Activity", secondary=organization_activity, back_populates="organizations"
    )
