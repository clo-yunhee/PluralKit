from datetime import datetime

import dateparser

from pluralkit import utils
from pluralkit.bot import errors, success
from pluralkit.bot.utils import CommandContext, ensure_system
from pluralkit.utils import humanize_delta


@ensure_system
async def switch_member(ctx: CommandContext):
    if not ctx.has_arg():
        raise errors.NoMembersSpecified()

    # Fetch a list of members from the command parameters
    members = []
    while ctx.has_arg():
        members.append(await ctx.pop_member())

    # Compare requested switch IDs and existing fronter IDs to check for existing switches
    # Lists, because order matters, it makes sense to just swap fronters
    member_ids = [member.id for member in members]
    past_fronter_ids = (await utils.get_fronter_ids(ctx.conn, ctx.system.id))[0]
    if member_ids == past_fronter_ids:
        raise errors.MembersAlreadyFronting([m.name for m in members])

    # Also make sure there aren't any duplicates
    if len(set(member_ids)) != len(member_ids):
        raise errors.DuplicateSwitchMembers()

    # Finally, log it
    async with ctx.conn.transaction():
        switch_id = await ctx.conn.add_switch(ctx.system.id)
        for member in members:
            await ctx.conn.add_switch_member(switch_id, member.id)

    return success.SwitchRegistered([m.name for m in members])


@ensure_system
async def switch_move(ctx: CommandContext):
    if not ctx.has_arg():
        raise errors.NotEnoughArgumentsProvided()

    new_time = dateparser.parse(ctx.args, languages=["en"], settings={"TO_TIMEZONE": "UTC", "RETURN_AS_TIMEZONE_AWARE": False})
    if not new_time:
        raise errors.InvalidTime(ctx.args)

    if new_time > datetime.utcnow():
        raise errors.CannotMoveSwitchToFuture()

    # Make sure it all runs in a big transaction for atomicity
    async with ctx.conn.transaction():
        # Get the last two switches to make sure the switch to move isn't before the second-last switch
        last_two_switches = await utils.get_front_history(ctx.conn, ctx.system.id, count=2)
        if len(last_two_switches) == 0:
            raise errors.NoSwitches()

        last_timestamp, last_fronters = last_two_switches[0]
        if len(last_two_switches) > 1:
            second_last_timestamp, _ = last_two_switches[1]

            if new_time < second_last_timestamp:
                raise errors.CannotMoveSwitchBeforeLast(second_last_timestamp)

        # Display the confirmation message w/ humanized times
        members = ", ".join([member.name for member in last_fronters]) or "nobody"
        last_absolute = last_timestamp.isoformat(sep=" ", timespec="seconds")
        last_relative = humanize_delta(last_timestamp)
        new_absolute = new_time.isoformat(sep=" ", timespec="seconds")
        new_relative = humanize_delta(new_time)

        if await ctx.confirm("This will move the latest switch ({}) from {} ({} ago) to {} ({} ago). Is this OK?".format(members, last_absolute, last_relative, new_absolute, new_relative)):
            # DB requires the actual switch ID which our utility method above doesn't return, fetch this manually
            switch_id = (await ctx.conn.front_history(ctx.system.id, count=1))[0]["id"]

            # Change the switch in the DB
            await ctx.conn.move_last_switch(ctx.system.id, switch_id, new_time)
        else:
            raise errors.ConfirmCancelled()
    return success.SwitchMoved()
