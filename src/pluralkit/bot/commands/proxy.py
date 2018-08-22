from pluralkit.bot import errors, success
from pluralkit.bot.utils import ensure_system, CommandContext


@ensure_system
async def member_proxy(ctx: CommandContext):
    member = await ctx.pop_member()

    prefix, suffix = None, None
    if ctx.has_arg():
        example = ctx.args

        # Check validity
        if "text" not in example or example.count("text") != 1:
            raise errors.InvalidExampleProxy()

        # Extract prefix/suffix
        prefix = example[:example.index("text")].strip() or None
        suffix = example[example.index("text") + 4:].strip() or None

    # Update in database
    async with ctx.conn.transaction():
        await ctx.conn.update_member_field(member.id, "prefix", prefix)
        await ctx.conn.update_member_field(member.id, "suffix", suffix)

    return success.ProxySettingsUpdated(bool(prefix or suffix))

