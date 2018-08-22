import asyncio
import os
import unittest
from unittest.mock import MagicMock

import discord

from pluralkit.bot.utils import CommandContext
from pluralkit.db import Database


def async_test(f):
    def wrapper(*args, **kwargs):
        future = f(*args, **kwargs)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(future)

    return wrapper


def async_return(obj):
    f = asyncio.Future()
    f.set_result(obj)
    return f


def mock_user(id, name=None, disc=None):
    user_mock = MagicMock()
    user_mock.id = id
    user_mock.name = name
    user_mock.discriminator = disc
    return user_mock


async def ctx(conn, sender, args="", channel=None, confirm=None, users=None):
    system = await conn.get_system_by_account(sender.id)

    client_mock = mock_client(users)

    ctx = CommandContext(conn, client_mock, channel, args, system, sender)
    if confirm is not None:
        ctx.confirm = MagicMock()
        ctx.confirm.return_value = async_return(confirm)

        ctx.confirm_with_string = MagicMock()
        ctx.confirm_with_string.return_value = async_return(confirm)

    return ctx


def mock_client(users=None):
    mock = MagicMock()
    if not users:
        users = {}

    def get_user(id):
        user = users.get(id)

        if user:
            return mock_user(id, name=user.get("name"), disc=user.get("disc"))

    async def get_user_info(id):
        mock = MagicMock()
        mock.status = ""
        raise discord.NotFound(mock, "")

    mock.get_user.side_effect = get_user
    mock.get_user_info.side_effect = get_user_info

    return mock

class DBTestCase(unittest.TestCase):
    @classmethod
    @async_test
    async def setUpClass(cls):
        db_user = os.environ["DATABASE_USER"]
        db_pass = os.environ["DATABASE_PASS"]
        db_host = os.environ["DATABASE_HOST"]
        db_port = int(os.environ["DATABASE_PORT"])
        db_name = "test"

        cls.db = Database(user=db_user, password=db_pass, host=db_host, port=db_port, database=db_name)
        await cls.db.__aenter__()

    @classmethod
    @async_test
    async def tearDownClass(cls):
        await cls.db.__aexit__(None, None, None)

    @async_test
    async def setUp(self):
        self.conn = await self.db.get_raw()
        await self.conn.clear_tables()
        await self.conn.create_tables()

    @async_test
    async def tearDown(self):
        await self.db.release_raw(self.conn)
