import discord

from pluralkit import System, Member
from pluralkit.db import DatabaseConnection
from pluralkit.utils import get_fronters, humanize_delta, escape


async def system_card(conn: DatabaseConnection, client: discord.Client, system: System) -> discord.Embed:
    card = discord.Embed()
    card.colour = discord.Colour.blue()

    if system.name:
        card.title = system.name

    if system.avatar_url:
        card.set_thumbnail(url=system.avatar_url)

    if system.tag:
        card.add_field(name="Tag", value=system.tag)

    fronters, switch_time = await get_fronters(conn, system.id)
    if fronters:
        names = ", ".join([member.name for member in fronters])
        fronter_val = "{} (for {})".format(names, humanize_delta(switch_time))
        card.add_field(name="Current fronter" if len(fronters) == 1 else "Current fronters", value=fronter_val)

    account_names = []
    for account_id in await conn.get_linked_accounts(system_id=system.id):
        # First try the local cache, then do a full lookup
        account = client.get_user(account_id)
        if not account:
            try:
                account = await client.get_user_info(account_id)
            except discord.NotFound:
                account = None

        if account:
            account_names.append("{}#{}".format(account.name, account.discriminator))
        else:
            account_names.append("<unknown account {}>".format(account_id))
    card.add_field(name="Linked accounts", value="\n".join(account_names))

    if system.description:
        card.add_field(name="Description",
                       value=system.description, inline=False)

    # Get names of all members
    member_texts = []
    for member in await conn.get_all_members(system_id=system.id):
        member_texts.append("{} (`{}`)".format(escape(member.name), member.hid))

    if len(member_texts) > 0:
        card.add_field(name="Members", value="\n".join(
            member_texts), inline=False)

    card.set_footer(text="System ID: {}".format(system.hid))
    return card


async def member_card(conn: DatabaseConnection, member: Member) -> discord.Embed:
    system = await conn.get_system(system_id=member.system)

    card = discord.Embed()
    card.colour = discord.Colour.blue()

    name_and_system = member.name
    if system.name:
        name_and_system += " ({})".format(system.name)

    card.set_author(name=name_and_system, icon_url=member.avatar_url or discord.Embed.Empty)
    if member.avatar_url:
        card.set_thumbnail(url=member.avatar_url)

    # Get system name and hid
    system = await conn.get_system(system_id=member.system)

    if member.color:
        card.colour = int(member.color, 16)

    if member.birthday:
        bday_val = member.birthday.strftime("%b %d, %Y")
        if member.birthday.year == 1:
            bday_val = member.birthday.strftime("%b %d")
        card.add_field(name="Birthdate", value=bday_val)

    if member.pronouns:
        card.add_field(name="Pronouns", value=member.pronouns)

    if member.prefix or member.suffix:
        prefix = member.prefix or ""
        suffix = member.suffix or ""
        card.add_field(name="Proxy Tags",
                       value="{}text{}".format(prefix, suffix))

    if member.description:
        card.add_field(name="Description",
                       value=member.description, inline=False)

    card.set_footer(text="System ID: {} | Member ID: {}".format(
        system.hid, member.hid))
    return card
