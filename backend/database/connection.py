from prisma import Prisma

class DBConnection:
    def __init__(self):
        self.db = Prisma()

    async def connect(self):
        await self.db.connect()
        return self.db

    async def disconnect(self):
        await self.db.disconnect()

conn_manager = DBConnection()

async def get_db():
    db = await conn_manager.connect()
    try:
        yield db
    finally:
        await conn_manager.disconnect()
        