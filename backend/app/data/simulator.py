"""Traffic data and accident simulator for development/testing."""
import asyncio
import random
import logging
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
logger = logging.getLogger(__name__)


async def seed_accident_data(session, count: int = 200):
    """Generate synthetic accident reports for development."""
    from app.db.models import AccidentReport, AccidentSeverity, AccidentSource
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point

    # Focus on a realistic urban grid (approximate major city coords)
    BASE_LAT, BASE_LNG = 51.5074, -0.1278  # London as default
    severities = list(AccidentSeverity)
    sources = [AccidentSource.CONFIRMED, AccidentSource.USER]

    records = []
    for _ in range(count):
        lat = BASE_LAT + random.uniform(-0.15, 0.15)
        lng = BASE_LNG + random.uniform(-0.15, 0.15)
        sev = random.choices(severities, weights=[40, 30, 20, 10])[0]
        days_ago = random.randint(0, 365)
        ts = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))

        records.append(AccidentReport(
            location=from_shape(Point(lng, lat), srid=4326),
            lat=lat, lng=lng,
            severity=sev,
            source=random.choice(sources),
            is_confirmed=(sev != AccidentSeverity.LOW),
            description=fake.sentence(nb_words=8),
            risk_score=random.uniform(10, 95),
            weather_condition=random.choice(["Clear", "Rain", "Fog", "Cloudy"]),
            timestamp=ts,
        ))

    session.add_all(records)
    await session.commit()
    logger.info(f"Seeded {count} accident records.")


async def seed_ambulance_fleet(session, count: int = 10):
    """Seed simulated ambulance fleet."""
    from app.db.models import Ambulance, AmbulanceStatus

    BASE_LAT, BASE_LNG = 51.5074, -0.1278
    hospitals = [
        "City General Hospital", "St. Mary Medical Centre",
        "North District Hospital", "Central Emergency Hospital",
        "South Medical Institute",
    ]

    records = []
    for i in range(1, count + 1):
        lat = BASE_LAT + random.uniform(-0.1, 0.1)
        lng = BASE_LNG + random.uniform(-0.1, 0.1)
        records.append(Ambulance(
            unit_code=f"AMB-{i:03d}",
            status=AmbulanceStatus.AVAILABLE,
            current_lat=lat,
            current_lng=lng,
            hospital_base=random.choice(hospitals),
            crew_count=random.choice([2, 3]),
            is_simulated=True,
        ))

    session.add_all(records)
    await session.commit()
    logger.info(f"Seeded {count} simulated ambulance units.")


async def main():
    from app.db.database import init_db, AsyncSessionLocal
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_accident_data(session, 200)
        await seed_ambulance_fleet(session, 10)
    logger.info("Data seeding complete.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
