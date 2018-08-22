from pluralkit.bot import errors, utils, success, cards
from pluralkit.bot.utils import ensure_system, CommandContext, validate_url


@ensure_system
async def member_new(ctx: CommandContext):
    if not ctx.has_arg():
        raise errors.NotEnoughArgumentsProvided()

    member_name = ctx.args  # TODO: remove quotes if accidentally added

    # Check for duplicate and confirm
    existing_member = await ctx.conn.get_member_by_name(ctx.system.id, member_name)
    if existing_member:
        if not await ctx.confirm("You already have a member with the name '{}' registered (ID: {}). Do you want to create a duplicate member?"):
            raise errors.ConfirmCancelled()

    hid = utils.generate_hid()
    await ctx.conn.create_member(ctx.system.id, member_name, hid)
    return success.MemberCreated(member_name, hid)


async def member_info(ctx: CommandContext):
    member = await ctx.pop_member(own_system_only=False)
    return await cards.member_card(ctx.conn, member)


@ensure_system
async def member_delete(ctx: CommandContext):
    member = await ctx.pop_member()

    if await ctx.confirm_with_string("Are you sure you want to delete '{}'? If so, reply to this message with the member's ID: {}".format(member.name, member.hid), member.hid):
        await ctx.conn.delete_member(member.id)
        return success.MemberDeleted()
    raise errors.ConfirmCancelled()


@ensure_system
async def member_name(ctx: CommandContext):
    member = await ctx.pop_member()

    if not ctx.args:
        raise errors.NotEnoughArgumentsProvided()

    await ctx.conn.update_member_field(member.id, "name", ctx.args)
    return success.NameSet(True)


@ensure_system
async def member_description(ctx: CommandContext):
    member = await ctx.pop_member()

    description = ctx.args or None
    await ctx.conn.update_member_field(member.id, "description", description)
    return success.DescriptionSet(bool(description))


@ensure_system
async def member_avatar(ctx: CommandContext):
    member = await ctx.pop_member()

    url = None
    args = ctx.args
    if ctx.args:
        try:
            account = await ctx.pop_account()
            url = account.avatar_url_as(format="png")
        except errors.AccountNotFound:
            url = args
            if not validate_url(url):
                raise errors.InvalidAvatarURL()

    await ctx.conn.update_member_field(member.id, "avatar_url", url)
    return success.AvatarSet(url)
