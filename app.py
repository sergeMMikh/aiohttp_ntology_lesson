import json

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


def raise_error(exception_class, message):
    raise exception_class(
        text=json.dumps({'status': 'error',
                        'message': message}),
        content_type='application/json'
    )


async def get_orm_item(orm_class, object_id, session):
    item = await session.get(orm_class, object_id)
    if item is None:
        raise raise_error(web.HTTPNotFound,
                          f'{orm_class.__name__} not found')
    return item


async def login(request: web.Request):
    return web.json_response({})


class UsersView(web.View):
    async def get(self):
        user_id = int(self.request.match_info['user_id'])
        user = await get_orm_item(User, user_id, self.request['session'])
        return web.json_response({
            'id': user.id,
            'name': user.name
        })

    async def post(self):
        user_data = await self.request.json()
        user_data['password'] = hash_password(user_data['password'])
        new_user = User(**user_data)
        self.request['session'].add(new_user)
        await self.request['session'].commit()
        return web.json_response({
            'id': new_user.id
        })

    async def patch(self):
        return web.json_response({})

    async def delete(self):
        return web.json_response({})


app = web.Application(middlewares=[session_middleware, ])
app._cleanup_ctx.append(app_context)

app.add_routes([
    web.post('/users/', UsersView),
    web.get('/users/{user_id:\d+}', UsersView),
])

if __name__ == '__main__':
    web.run_app(app, port=8080)
