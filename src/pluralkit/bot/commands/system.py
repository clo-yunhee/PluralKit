from pluralkit.bot import errors, success, cards
from pluralkit.bot.utils import CommandContext, generate_hid, ensure_system, ensure_no_system, validate_url


async def system_info(ctx: CommandContext):
    if ctx.has_arg():
        system = await ctx.pop_system()
    else:
        system = ctx.system
        if not system:
            raise errors.NoRegisteredSystem()

    return await cards.system_card(ctx.conn, ctx.client, system)


@ensure_no_system
async def system_register(ctx: CommandContext):
    name = ctx.args or None

    async with ctx.conn.transaction():
        hid = generate_hid()
        system = await ctx.conn.create_system(name, hid)
        await ctx.conn.link_account(system.id, ctx.sender.id)

        return success.SystemRegistered()


@ensure_system
async def system_link(ctx: CommandContext):
    account = await ctx.pop_account()

    current_account_system = await ctx.conn.get_system_by_account(account.id)
    if current_account_system:
        raise errors.LinkeeAlreadyInSystem(current_account_system.hid)

    if await ctx.confirm("{}, please confirm the link by reacting to this message.".format(account.mention), user_to_confirm=account):
        await ctx.conn.link_account(ctx.system.id, account.id)

        return success.SystemLinked()
    else:
        raise errors.ConfirmCancelled()


@ensure_system
async def system_unlink(ctx: CommandContext):
    linked_accounts = await ctx.conn.get_linked_accounts(ctx.system.id)
    if len(linked_accounts) == 1:
        raise errors.CannotUnlinkOnlyAccount()

    await ctx.conn.unlink_account(ctx.system.id, ctx.sender.id)


@ensure_system
async def system_delete(ctx: CommandContext):
    if await ctx.confirm_with_string("Are you sure you want to delete your system? If so, reply to this message with your system ID: {}".format(ctx.system.hid), ctx.system.hid):
        await ctx.conn.delete_system(ctx.system.id)
        return success.SystemDeleted()
    else:
        raise errors.ConfirmCancelled()


@ensure_system
async def system_description(ctx: CommandContext):
    description = ctx.args or None
    await ctx.conn.update_system_field(ctx.system.id, "description", description)
    return success.DescriptionSet(bool(description))


@ensure_system
async def system_name(ctx: CommandContext):
    name = ctx.args or None
    await ctx.conn.update_system_field(ctx.system.id, "name", name)
    return success.NameSet(bool(name))


@ensure_system
async def system_tag(ctx: CommandContext):
    tag = ctx.args or None
    await ctx.conn.update_system_field(ctx.system.id, "tag", tag)
    return success.TagSet(bool(tag))


@ensure_system
async def system_avatar(ctx: CommandContext):
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

    await ctx.conn.update_system_field(ctx.system.id, "avatar_url", url)
    return success.AvatarSet(url)
