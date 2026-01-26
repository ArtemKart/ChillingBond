import asyncio
import random
from decimal import Decimal

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import text, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.outbound.database import Base
from src.adapters.outbound.database.models import User as UserModel
from src.adapters.outbound.database.models import Bond as BondModel
from src.adapters.outbound.database.models import BondHolder as BondholderModel
from src.adapters.outbound.security.bcrypt_hasher import BcryptPasswordHasher


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/loadtest_db"
NUM_USERS = 10
BONDS_QUANTITY = 15
BONDHOLDERS_PER_USER = 10

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    pool_pre_ping=True,
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def setup_load_test_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        users = await _load_users()
        bonds = await _load_bonds()
        await _load_bondholders(users=users, bonds=bonds)

        print("\n🔍 Verifying data...")
        async with async_session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM user"))
            user_count = result.scalar()

            result = await session.execute(text("SELECT COUNT(*) FROM bond"))
            bond_count = result.scalar()

            result = await session.execute(text("SELECT COUNT(*) FROM bondholder"))
            bondholder_count = result.scalar()

        print("\n" + "=" * 60)
        print("✅ Load test database setup completed!")
        print("=" * 60)
        print("\n📊 Statistics:")
        print(f"   Users: {user_count}")
        print(f"   Bonds: {bond_count}")
        print(f"   BondHolders: {bondholder_count}")
        print("\n🔐 Test credentials:")
        print(f"   Email: loadtest0@example.com ... loadtest{NUM_USERS-1}@example.com")
        print("   Password: LoadTest123!")
        print("\n🚀 Ready to run load tests!")
        print(
            "   Command: locust -f tests/load/locustfile.py --host=http://localhost:8001"
        )

    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        raise
    finally:
        await engine.dispose()


async def _load_users() -> list[UserModel]:
    hasher = BcryptPasswordHasher()
    async with async_session() as session:
        users = [
            UserModel(
                id=uuid4(),
                email=f"loadtest{i}@example.com",
                password=hasher.hash("LoadTest123!"),
                name=None,
            )
            for i in range(NUM_USERS)
        ]
        session.add_all(users)
        await session.commit()
    print(f"   ✅ {len(users)} users created")
    return users


async def _load_bonds() -> list[BondModel]:
    nominal_values = [100, 200, 300, 400, 500]
    async with async_session() as session:
        bonds = [
            BondModel(
                id=uuid4(),
                nominal_value=Decimal(random.choice(nominal_values)),
                series=f"ROR{i}",
                maturity_period=12,
                initial_interest_rate=Decimal(5.0),
                first_interest_period=1,
                reference_rate_margin=Decimal(0.1),
            )
            for i in range(BONDS_QUANTITY)
        ]
        session.add_all(bonds)
        await session.commit()

    print(f"   ✅ {len(bonds)} bonds created")
    return bonds


async def _load_bondholders(
    users: list[UserModel], bonds: list[BondModel]
) -> list[BondholderModel]:
    async with async_session() as session:
        bondholders = [
            BondholderModel(
                id=uuid4(),
                user_id=user.id,
                bond_id=random.choice(bonds).id,
                quantity=random.randint(50, 100),
                purchase_date=datetime.now(timezone.utc),
                last_update=None,
            )
            for _ in range(BONDHOLDERS_PER_USER)
            for user in users
        ]
        session.add_all(bondholders)
        await session.commit()

    print(f"   ✅ {len(bondholders)} bondholders created")
    return bondholders


if __name__ == "__main__":
    asyncio.run(setup_load_test_database())
