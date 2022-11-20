from aiohttp import web
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from typing import Callable, Awaitable

from config import PG_DSN
from models import Base, User, Token
from auth import hash_password, check_password

engine = create_async_engine(PG_DSN)

Session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

@web.middleware
async def session_middleware(request: web.Request,
                             handler: Callable[[web.Request],
                                               Awaitable[web.Response]]):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)

        return response


async def app_context(app: web.Application):
    async with engine.begin() as conn:
        async with Session() as session:
            await session.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            await session.commit()
        await conn.run_sync(Base.metadata.create_all)
    print('START')
    yield
    await engine.dispose()
    print("FINISH")


async def login(request: web.Request):
    return web.json_response({})


class Users(web.View):
    async def get(self):
        return web.json_response({})

    async def post(self):
        user_data = await self.request.json()
        user_data['password'] = hash_password(user_data['password'])

        return web.json_response({})

    async def patch(self):
        return web.json_response({})

    async def delete(self):
        return web.json_response({})


app = web.Application(middlewares=[session_middleware, ])
app._cleanup_ctx.append(app_context)

if __name__ == '__main__':
    web.run_app(app, port=8080)
