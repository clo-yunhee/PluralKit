import asyncio
import random
import re
import string
from typing import Tuple, Optional, Union
from urllib.parse import urlparse

import aiohttp
import discord

from pluralkit import System, Member
from pluralkit.bot import errors
from pluralkit.db import DatabaseConnection


class CommandContext:
    conn: DatabaseConnection
    client: discord.Client
    channel: discord.abc.Messageable
    args: str
    system: Optional[System]
    sender: discord.Member

    def __init__(self, conn, client, channel, args, system, sender):
        self.conn = conn
        self.client = client
        self.channel = channel
        self.args = args
        self.system = system
        self.sender = sender

    def has_arg(self):
        return bool(self.args)

    def pop_arg(self):
        if not self.has_arg():
            raise errors.NotEnoughArgumentsProvided()

        new_arg, self.args = next_arg(self.args)
        return new_arg

    def peek_arg(self):
        if not self.has_arg():
            raise errors.NotEnoughArgumentsProvided()
        new_arg, _ = next_arg(self.args)
        return new_arg

    async def pop_system(self) -> System:
        system_name = self.pop_arg()
        return await param_system(self.conn, self.client, system_name)

    async def pop_member(self, own_system_only=True) -> Member:
        if own_system_only and not self.system:
            raise errors.NoRegisteredSystem()

        member_name = self.pop_arg()
        return await param_member(self.conn, self.system, member_name, enforce_system=own_system_only)

    async def pop_account(self) -> discord.User:
        account_name = self.pop_arg()

        account = await parse_mention(self.client, account_name)
        if not account:
            raise errors.AccountNotFound(account_name)
        return account

    async def send(self, content):
        await self.channel.send(content)

    async def send_embed(self, embed):
        await self.channel.send(embed=embed)

    async def send_help(self, help_page, content):
        await self.channel.send(content)
        # TODO

    async def confirm(self, text, user_to_confirm=None):
        user_to_confirm = user_to_confirm or self.sender

        message: discord.Message = await self.channel.send(text)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def pred(reaction, user):
            return user.id == user_to_confirm.id and reaction.emoji in ["✅", "❌"]

        try:
            reaction, user = await self.client.wait_for("reaction_add", check=pred, timeout=60)
            return reaction.emoji == "✅"
        except asyncio.TimeoutError:
            raise errors.ConfirmTimedOut()

    async def confirm_with_string(self, text, string_to_confirm, user_to_confirm=None):
        user_to_confirm = user_to_confirm or self.sender

        await self.channel.send(text)

        def pred(message):
            return message.author.id == user_to_confirm.id

        try:
            message = await self.client.wait_for("message", check=pred, timeout=60)
            return message.content == string_to_confirm
        except asyncio.TimeoutError:
            raise errors.ConfirmTimedOut()


def next_arg(arg_string: str) -> Tuple[str, Optional[str]]:
    if arg_string.startswith("\""):
        end_quote = arg_string.find("\"", start=1)
        if end_quote > 0:
            return arg_string[1:end_quote], arg_string[end_quote + 1:].strip()
        else:
            return arg_string[1:], None

    next_space = arg_string.find(" ")
    if next_space >= 0:
        return arg_string[:next_space].strip(), arg_string[next_space:].strip()
    else:
        return arg_string.strip(), None


async def parse_mention(client: discord.Client, mention: str) -> Optional[discord.User]:
    # First try matching mention format
    match = re.fullmatch("<@!?(\\d+)>", mention)
    if match:
        user_id = int(match.group(1))
    else:
        # If not, try plain ID
        try:
            user_id = int(mention)
        except ValueError:
            return None

    # First try the ID in the client user cache
    user = client.get_user(user_id)
    if user:
        return user

    # If not found in cache, do full lookup
    try:
        return await client.get_user_info(user_id)
    except discord.NotFound:
        return None


async def param_system(conn: DatabaseConnection, client: discord.Client, param: str, throw: bool = True) -> System:
    # First try to look up by system ID
    system = await conn.get_system_by_hid(param)
    if system:
        return system

    # Then try to look up by Discord member
    account = await parse_mention(client, param)
    if account:
        system = await conn.get_system_by_account(account.id)
        if system:
            return system

    # Nope, didn't find anything
    if throw:
        raise errors.SystemParamNotFound(param)


async def param_member(conn: DatabaseConnection, system: System, member_name: str, enforce_system: bool = True, throw: bool = True) -> Member:
    # First look up by member ID
    member = await conn.get_member_by_hid(member_name)
    if member and (not enforce_system or member.system == system.id):
        return member

    # Then look up by name in system
    if not system:
        # Can't look up if no system is specified here
        if throw:
            raise errors.MemberParamNotFound(member_name)
        return None

    member = await conn.get_member_by_name(system.id, member_name)
    if not member and throw:
        raise errors.MemberParamNotFound(member_name)

    return member


async def sender_system(conn: DatabaseConnection, sender: Union[discord.Member, discord.User]) -> System:
    system = await conn.get_system_by_account(sender.id)
    if not system:
        raise errors.NoRegisteredSystem()
    return system


def generate_hid() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=5))


def ensure_system(f):
    async def inner(ctx: CommandContext, *args, **kwargs):
        if not ctx.system:
            raise errors.NoRegisteredSystem()
        return await f(ctx, *args, **kwargs)

    return inner


def ensure_no_system(f):
    async def inner(ctx: CommandContext, *args, **kwargs):
        if ctx.system:
            raise errors.AlreadyRegisteredSystem()
        return await f(ctx, *args, **kwargs)

    return inner


def validate_url(url: str) -> bool:
    u = urlparse(url)
    return u.scheme in ["http", "https"] and u.netloc and u.path