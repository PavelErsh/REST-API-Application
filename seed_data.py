"""
Script to populate the database with test data
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models


def seed_data():
    db = SessionLocal()

    try:
        # Create Buildings
        print("Creating buildings...")
        buildings = [
            models.Building(
                address="г. Москва, ул. Ленина 1, офис 3",
                latitude=55.751244,
                longitude=37.618423,
            ),
            models.Building(
                address="г. Москва, ул. Блюхера, 32/1",
                latitude=55.756244,
                longitude=37.625423,
            ),
            models.Building(
                address="г. Санкт-Петербург, Невский проспект, 28",
                latitude=59.934280,
                longitude=30.335099,
            ),
            models.Building(
                address="г. Новосибирск, ул. Красный проспект, 99",
                latitude=55.030204,
                longitude=82.920430,
            ),
        ]
        db.add_all(buildings)
        db.commit()

        # Refresh to get IDs
        for building in buildings:
            db.refresh(building)

        print(f"Created {len(buildings)} buildings")

        # Create Activities (Tree structure with max 3 levels)
        print("Creating activities...")

        # Level 1 activities
        food = models.Activity(name="Еда", level=1)
        automobiles = models.Activity(name="Автомобили", level=1)
        services = models.Activity(name="Услуги", level=1)

        db.add_all([food, automobiles, services])
        db.commit()
        db.refresh(food)
        db.refresh(automobiles)
        db.refresh(services)

        # Level 2 activities (children of Level 1)
        meat = models.Activity(name="Мясная продукция", parent_id=food.id, level=2)
        dairy = models.Activity(name="Молочная продукция", parent_id=food.id, level=2)
        bakery = models.Activity(
            name="Хлебобулочные изделия", parent_id=food.id, level=2
        )

        trucks = models.Activity(name="Грузовые", parent_id=automobiles.id, level=2)
        passenger = models.Activity(name="Легковые", parent_id=automobiles.id, level=2)

        cleaning = models.Activity(name="Клининг", parent_id=services.id, level=2)
        repair = models.Activity(name="Ремонт", parent_id=services.id, level=2)

        db.add_all([meat, dairy, bakery, trucks, passenger, cleaning, repair])
        db.commit()

        # Refresh level 2 activities
        for activity in [meat, dairy, bakery, trucks, passenger, cleaning, repair]:
            db.refresh(activity)

        # Level 3 activities (children of Level 2)
        parts = models.Activity(name="Запчасти", parent_id=passenger.id, level=3)
        accessories = models.Activity(
            name="Аксессуары", parent_id=passenger.id, level=3
        )

        db.add_all([parts, accessories])
        db.commit()
        db.refresh(parts)
        db.refresh(accessories)

        print("Created activity tree with 3 levels")

        # Create Organizations
        print("Creating organizations...")

        org1 = models.Organization(
            name='ООО "Рога и Копыта"', building_id=buildings[1].id
        )
        org1.activities.extend([meat, dairy])
        db.add(org1)
        db.commit()
        db.refresh(org1)

        # Add phone numbers for org1
        phone1_1 = models.PhoneNumber(number="2-222-222", organization_id=org1.id)
        phone1_2 = models.PhoneNumber(number="3-333-333", organization_id=org1.id)
        phone1_3 = models.PhoneNumber(number="8-923-666-13-13", organization_id=org1.id)
        db.add_all([phone1_1, phone1_2, phone1_3])

        org2 = models.Organization(
            name='ООО "Молочный Завод"', building_id=buildings[0].id
        )
        org2.activities.append(dairy)
        db.add(org2)
        db.commit()
        db.refresh(org2)

        phone2_1 = models.PhoneNumber(number="8-495-123-45-67", organization_id=org2.id)
        phone2_2 = models.PhoneNumber(number="8-800-555-35-35", organization_id=org2.id)
        db.add_all([phone2_1, phone2_2])

        org3 = models.Organization(
            name='АО "Мясокомбинат"', building_id=buildings[0].id
        )
        org3.activities.extend([meat, food])
        db.add(org3)
        db.commit()
        db.refresh(org3)

        phone3_1 = models.PhoneNumber(number="8-495-777-88-99", organization_id=org3.id)
        db.add(phone3_1)

        org4 = models.Organization(
            name='ИП "Автозапчасти Плюс"', building_id=buildings[2].id
        )
        org4.activities.extend([parts, accessories, passenger])
        db.add(org4)
        db.commit()
        db.refresh(org4)

        phone4_1 = models.PhoneNumber(number="8-812-300-40-50", organization_id=org4.id)
        phone4_2 = models.PhoneNumber(number="8-812-300-40-51", organization_id=org4.id)
        db.add_all([phone4_1, phone4_2])

        org5 = models.Organization(
            name='ООО "Грузовой Парк"', building_id=buildings[3].id
        )
        org5.activities.append(trucks)
        db.add(org5)
        db.commit()
        db.refresh(org5)

        phone5_1 = models.PhoneNumber(number="8-383-222-33-44", organization_id=org5.id)
        db.add(phone5_1)

        org6 = models.Organization(name='ООО "Чистый Дом"', building_id=buildings[1].id)
        org6.activities.extend([cleaning, services])
        db.add(org6)
        db.commit()
        db.refresh(org6)

        phone6_1 = models.PhoneNumber(number="8-495-111-22-33", organization_id=org6.id)
        db.add(phone6_1)

        org7 = models.Organization(
            name='ИП "Пекарня У Дома"', building_id=buildings[2].id
        )
        org7.activities.extend([bakery, food])
        db.add(org7)
        db.commit()
        db.refresh(org7)

        phone7_1 = models.PhoneNumber(number="8-812-999-88-77", organization_id=org7.id)
        db.add(phone7_1)

        db.commit()

        print("Created 7 organizations with phone numbers")
        print("\nTest data seeded successfully!")
        print("\nSummary:")
        print(f"- Buildings: {db.query(models.Building).count()}")
        print(f"- Activities: {db.query(models.Activity).count()}")
        print(f"- Organizations: {db.query(models.Organization).count()}")
        print(f"- Phone Numbers: {db.query(models.PhoneNumber).count()}")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting database seeding...")
    seed_data()
