import asyncio
import logging
from collections import namedtuple
from datetime import datetime
from typing import List

import asyncpg
import asyncpg.exceptions
from discord.utils import snowflake_time

from pluralkit import System, Member


class ProxyMember(namedtuple("ProxyMember",
                             ["id", "hid", "prefix", "suffix", "color", "name", "avatar_url", "tag", "system_name",
                              "system_hid"])):
    id: int
    hid: str
    prefix: str
    suffix: str
    color: str
    name: str
    avatar_url: str
    tag: str
    system_name: str
    system_hid: str

    def full_name(self):
        if self.tag:
            return "{} {}".format(self.name, self.tag)
        return self.name


class MessageInfo(namedtuple("MemberInfo",
                             ["mid", "channel", "member", "content", "sender", "name", "hid", "avatar_url",
                              "system_name", "system_hid"])):
    mid: int
    channel: int
    member: int
    content: str
    sender: int
    name: str
    hid: str
    avatar_url: str
    system_name: str
    system_hid: str

    def to_json(self):
        return {
            "id": str(self.mid),
            "channel": str(self.channel),
            "member": self.hid,
            "system": self.system_hid,
            "message_sender": str(self.sender),
            "content": self.content,
            "timestamp": snowflake_time(self.mid).isoformat()
        }


class DatabaseConnection:
    conn: asyncpg.Connection

    def __init__(self, conn):
        self.logger = logging.getLogger("pluralkit.db")
        self.conn = conn

    def transaction(self):
        return self.conn.transaction()

    async def create_system(self, system_name: str, system_hid: str) -> System:
        self.logger.debug("Creating system (name={}, hid={})".format(system_name, system_hid))
        row = await self.conn.fetchrow("insert into systems (name, hid) values ($1, $2) returning *", system_name,
                                       system_hid)
        return System(**row) if row else None

    async def delete_system(self, system_id: int):
        self.logger.debug("Deleting system (id={})".format(system_id))
        await self.conn.execute("delete from systems where id = $1", system_id)

    async def create_member(self, system_id: int, member_name: str, member_hid: str) -> Member:
        self.logger.debug("Creating member (system={}, name={}, hid={})".format(
            system_id, member_name, member_hid))
        row = await self.conn.fetchrow("insert into members (name, system, hid) values ($1, $2, $3) returning *",
                                       member_name, system_id, member_hid)
        return Member(**row) if row else None

    async def delete_member(self, member_id: int):
        self.logger.debug("Deleting member (id={})".format(member_id))
        await self.conn.execute("delete from members where id = $1", member_id)

    async def link_account(self, system_id: int, account_id: str):
        self.logger.debug("Linking account (account_id={}, system_id={})".format(
            account_id, system_id))
        await self.conn.execute("insert into accounts (uid, system) values ($1, $2)", int(account_id), system_id)

    async def unlink_account(self, system_id: int, account_id: str):
        self.logger.debug("Unlinking account (account_id={}, system_id={})".format(
            account_id, system_id))
        await self.conn.execute("delete from accounts where uid = $1 and system = $2", int(account_id), system_id)

    async def get_linked_accounts(self, system_id: int) -> List[int]:
        return [row["uid"] for row in await self.conn.fetch("select uid from accounts where system = $1", system_id)]

    async def get_system_by_account(self, account_id: int) -> System:
        row = await self.conn.fetchrow(
            "select systems.* from systems, accounts where accounts.uid = $1 and accounts.system = systems.id",
            account_id)
        return System(**row) if row else None

    async def get_system_by_hid(self, system_hid: str) -> System:
        row = await self.conn.fetchrow("select * from systems where hid = $1", system_hid)
        return System(**row) if row else None

    async def get_system(self, system_id: int) -> System:
        row = await self.conn.fetchrow("select * from systems where id = $1", system_id)
        return System(**row) if row else None

    async def get_member_by_name(self, system_id: int, member_name: str) -> Member:
        row = await self.conn.fetchrow("select * from members where system = $1 and lower(name) = lower($2)", system_id,
                                       member_name)
        return Member(**row) if row else None

    async def get_member_by_hid_in_system(self, system_id: int, member_hid: str) -> Member:
        row = await self.conn.fetchrow("select * from members where system = $1 and hid = $2", system_id, member_hid)
        return Member(**row) if row else None

    async def get_member_by_hid(self, member_hid: str) -> Member:
        row = await self.conn.fetchrow("select * from members where hid = $1", member_hid)
        return Member(**row) if row else None

    async def get_member(self, member_id: int) -> Member:
        row = await self.conn.fetchrow("select * from members where id = $1", member_id)
        return Member(**row) if row else None

    async def get_members(self, members: list) -> List[Member]:
        rows = await self.conn.fetch("select * from members where id = any($1)", members)
        return [Member(**row) for row in rows]

    async def update_system_field(self, system_id: int, field: str, value):
        self.logger.debug("Updating system field (id={}, {}={})".format(
            system_id, field, value))
        await self.conn.execute("update systems set {} = $1 where id = $2".format(field), value, system_id)

    async def update_member_field(self, member_id: int, field: str, value):
        self.logger.debug("Updating member field (id={}, {}={})".format(
            member_id, field, value))
        await self.conn.execute("update members set {} = $1 where id = $2".format(field), value, member_id)

    async def get_all_members(self, system_id: int) -> List[Member]:
        rows = await self.conn.fetch("select * from members where system = $1", system_id)
        return [Member(**row) for row in rows]

    async def get_members_exceeding(self, system_id: int, length: int) -> List[Member]:
        rows = await self.conn.fetch("select * from members where system = $1 and length(name) > $2", system_id, length)
        return [Member(**row) for row in rows]

    async def get_webhook(self, channel_id: int) -> (int, str):
        row = await self.conn.fetchrow("select webhook, token from webhooks where channel = $1", channel_id)
        return (row["webhook"], row["token"]) if row else None

    async def add_webhook(self, channel_id: int, webhook_id: int, webhook_token: str):
        self.logger.debug("Adding new webhook (channel={}, webhook={}, token={})".format(
            channel_id, webhook_id, webhook_token))
        await self.conn.execute("insert into webhooks (channel, webhook, token) values ($1, $2, $3)", channel_id,
                                webhook_id, webhook_token)

    async def delete_webhook(self, channel_id: str):
        await self.conn.execute("delete from webhooks where channel = $1", int(channel_id))

    async def add_message(self, message_id: int, channel_id: int, member_id: int, sender_id: int, content: str):
        self.logger.debug("Adding new message (id={}, channel={}, member={}, sender={})".format(
            message_id, channel_id, member_id, sender_id))
        await self.conn.execute(
            "insert into messages (mid, channel, member, sender, content) values ($1, $2, $3, $4, $5)",
            message_id, channel_id, member_id, sender_id, content)

    async def get_members_by_account(self, account_id: int) -> List[ProxyMember]:
        # Returns a "chimera" object
        rows = await self.conn.fetch("""select
                members.id, members.hid, members.prefix, members.suffix, members.color, members.name, members.avatar_url,
                systems.tag, systems.name as system_name, systems.hid as system_hid
            from
                systems, members, accounts
            where
                accounts.uid = $1
                and systems.id = accounts.system
                and members.system = systems.id""", account_id)
        return [ProxyMember(**row) for row in rows]

    async def get_message_by_sender_and_id(self, message_id: int, sender_id: int) -> MessageInfo:
        row = await self.conn.fetchrow("""select
            messages.*,
            members.name, members.hid, members.avatar_url,
            systems.name as system_name, systems.hid as system_hid
        from
            messages, members, systems
        where
            messages.member = members.id
            and members.system = systems.id
            and mid = $1
            and sender = $2""", message_id, sender_id)
        return MessageInfo(**row) if row else None

    async def get_message(self, message_id: str) -> MessageInfo:
        row = await self.conn.fetchrow("""select
            messages.*,
            members.name, members.hid, members.avatar_url,
            systems.name as system_name, systems.hid as system_hid
        from
            messages, members, systems
        where
            messages.member = members.id
            and members.system = systems.id
            and mid = $1""", int(message_id))
        return MessageInfo(**row) if row else None

    async def delete_message(self, message_id: int):
        self.logger.debug("Deleting message (id={})".format(message_id))
        await self.conn.execute("delete from messages where mid = $1", message_id)

    async def front_history(self, system_id: int, count: int):
        return await self.conn.fetch("""select
            switches.*,
            array(
                select member from switch_members
                where switch_members.switch = switches.id
                order by switch_members.id asc
            ) as members
        from switches
        where switches.system = $1
        order by switches.timestamp desc
        limit $2""", system_id, count)

    async def add_switch(self, system_id: int):
        self.logger.debug("Adding switch (system={})".format(system_id))
        res = await self.conn.fetchrow("insert into switches (system) values ($1) returning *", system_id)
        return res["id"]

    async def move_last_switch(self, system_id: int, switch_id: int, new_time: datetime):
        self.logger.debug("Moving latest switch (system={}, id={}, new_time={})".format(system_id, switch_id, new_time))
        await self.conn.execute("update switches set timestamp = $1 where system = $2 and id = $3", new_time, system_id,
                                switch_id)

    async def add_switch_member(self, switch_id: int, member_id: int):
        self.logger.debug("Adding switch member (switch={}, member={})".format(switch_id, member_id))
        await self.conn.execute("insert into switch_members (switch, member) values ($1, $2)", switch_id, member_id)

    async def get_server_info(self, server_id: str):
        return await self.conn.fetchrow("select * from servers where id = $1", int(server_id))

    async def update_server(self, server_id: str, logging_channel_id: str):
        logging_channel_id = int(logging_channel_id) if logging_channel_id else None
        self.logger.debug("Updating server settings (id={}, log_channel={})".format(server_id, logging_channel_id))
        await self.conn.execute(
            "insert into servers (id, log_channel) values ($1, $2) on conflict (id) do update set log_channel = $2",
            int(server_id), logging_channel_id)

    async def member_count(self) -> int:
        return await self.conn.fetchval("select count(*) from members")

    async def system_count(self) -> int:
        return await self.conn.fetchval("select count(*) from systems")

    async def message_count(self) -> int:
        return await self.conn.fetchval("select count(*) from messages")

    async def account_count(self) -> int:
        return await self.conn.fetchval("select count(*) from accounts")

    async def create_tables(self):
        await self.conn.execute("""create table if not exists systems (
            id          serial primary key,
            hid         char(5) unique not null,
            name        text,
            description text,
            tag         text,
            avatar_url  text,
            created     timestamp not null default current_timestamp
        )""")
        await self.conn.execute("""create table if not exists members (
            id          serial primary key,
            hid         char(5) unique not null,
            system      serial not null references systems(id) on delete cascade,
            color       char(6),
            avatar_url  text,
            name        text not null,
            birthday    date,
            pronouns    text,
            description text,
            prefix      text,
            suffix      text,
            created     timestamp not null default current_timestamp
        )""")
        await self.conn.execute("""create table if not exists accounts (
            uid         bigint primary key,
            system      serial not null references systems(id) on delete cascade
        )""")
        await self.conn.execute("""create table if not exists messages (
            mid         bigint primary key,
            channel     bigint not null,
            member      serial not null references members(id) on delete cascade,
            content     text not null,
            sender      bigint not null
        )""")
        await self.conn.execute("""create table if not exists switches (
            id          serial primary key,
            system      serial not null references systems(id) on delete cascade,
            timestamp   timestamp not null default current_timestamp
        )""")
        await self.conn.execute("""create table if not exists switch_members (
            id          serial primary key,
            switch      serial not null references switches(id) on delete cascade,
            member      serial not null references members(id) on delete cascade
        )""")
        await self.conn.execute("""create table if not exists webhooks (
            channel     bigint primary key,
            webhook     bigint not null,
            token       text not null
        )""")
        await self.conn.execute("""create table if not exists servers (
            id          bigint primary key,
            log_channel bigint
        )""")

    async def clear_tables(self):
        await self.conn.execute("drop table if exists systems cascade ")
        await self.conn.execute("drop table if exists members cascade ")
        await self.conn.execute("drop table if exists accounts cascade ")
        await self.conn.execute("drop table if exists messages cascade ")
        await self.conn.execute("drop table if exists switches cascade ")
        await self.conn.execute("drop table if exists switch_members cascade ")
        await self.conn.execute("drop table if exists webhooks cascade ")
        await self.conn.execute("drop table if exists servers cascade ")


class Database:
    logger: logging.Logger
    pool: asyncpg.pool.Pool

    user: str
    password: str
    host: str
    port: int
    database: str

    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        self.logger = logging.getLogger("pluralkit.db")
        pass

    async def __aenter__(self):
        while True:
            try:
                self.logger.info(
                    "Attempting a database connection to {}:<password>@{}:{}/{}...".format(self.user, self.host,
                                                                                           self.port, self.database))

                self.pool = await asyncpg.create_pool(
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port,
                    database=self.database
                )

                self.logger.info("Successfully connected to database.")
                return self
            except (ConnectionError, asyncpg.exceptions.CannotConnectNowError):
                self.logger.exception("Connection failed. Retrying in two seconds...")
                await asyncio.sleep(2)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Closing database connection.")
        await self.pool.close()

    def get(self):
        db = self

        class ConnectionContext:
            async def __aenter__(self):
                self.conn = await db.pool.acquire()
                return DatabaseConnection(self.conn)

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await db.pool.release(self.conn)

        return ConnectionContext()

    async def get_raw(self) -> DatabaseConnection:
        return DatabaseConnection(await self.pool.acquire())

    async def release_raw(self, conn: DatabaseConnection):
        await self.pool.release(conn.conn)

# def db_wrap(func):
#     async def inner(*args, **kwargs):
#         before = time.perf_counter()
#         try:
#             res = await func(*args, **kwargs)
#             after = time.perf_counter()
#
#             logger.debug(" - DB call {} took {:.2f} ms".format(func.__name__, (after - before) * 1000))
#             await stats.report_db_query(func.__name__, after - before, True)
#
#             return res
#         except asyncpg.exceptions.PostgresError:
#             await stats.report_db_query(func.__name__, time.perf_counter() - before, False)
#             logger.exception("Error from database query {}".format(func.__name__))
#     return inner
