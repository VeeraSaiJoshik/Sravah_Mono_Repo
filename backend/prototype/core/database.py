from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from prototype.core.config import settings
from prototype.models.database.user import User

class Database : 
    client: AsyncIOMotorClient = None

    @classmethod
    async def init_database(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        await init_beanie(
            database=cls.client["Development"], 
            document_models=[
                User
            ]
        )

        print("database has been connected")
    
    @classmethod
    async def terminate_db(cls):
        if cls.client :
            cls.client.drop_database()