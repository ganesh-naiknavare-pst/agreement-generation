from prisma import Prisma

class DBConnection:
    def __init__(self):
        self.db = Prisma()

    async def connect(self):
        await self.db.connect()

    async def disconnect(self):
        await self.db.disconnect()

conn_manager = DBConnection()

async def get_db():
    return conn_manager.db
