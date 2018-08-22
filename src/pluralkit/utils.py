from datetime import datetime, timedelta
from typing import List, Tuple, Union

from pluralkit import Member
from pluralkit.db import DatabaseConnection


async def get_fronter_ids(conn: DatabaseConnection, system_id: int) -> (List[int], datetime):
    switches = await conn.front_history(system_id=system_id, count=1)
    if not switches:
        return [], None

    if not switches[0]["members"]:
        return [], switches[0]["timestamp"]

    return switches[0]["members"], switches[0]["timestamp"]


async def get_fronters(conn: DatabaseConnection, system_id: int) -> (List[Member], datetime):
    member_ids, timestamp = await get_fronter_ids(conn, system_id)

    # Collect in dict and then look up as list, to preserve return order
    members = {member.id: member for member in await conn.get_members(member_ids)}
    return [members[member_id] for member_id in member_ids], timestamp


async def get_front_history(conn: DatabaseConnection, system_id: int, count: int) -> List[Tuple[datetime, List[Member]]]:
    # Get history from DB
    switches = await conn.front_history(system_id=system_id, count=count)
    if not switches:
        return []

    # Get all unique IDs referenced
    all_member_ids = {id for switch in switches for id in switch["members"]}

    # And look them up in the database into a dict
    all_members = {member.id: member for member in await conn.get_members(list(all_member_ids))}

    # Collect in array and return
    out = []
    for switch in switches:
        timestamp = switch["timestamp"]
        members = [all_members[id] for id in switch["members"]]
        out.append((timestamp, members))
    return out


def humanize_delta(delta: Union[timedelta, datetime]) -> str:
    if isinstance(delta, datetime):
        delta = datetime.utcnow() - delta

    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60

    if days:
        return "{}d {}h".format(days, hours)
    if hours:
        return "{}h {}m".format(hours, minutes)
    if minutes:
        return "{}m {}s".format(minutes, seconds)
    return "{}s".format(seconds)


def escape(s):
    return s.replace("`", "\\`")
