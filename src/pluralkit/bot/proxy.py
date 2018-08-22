import logging
import re
from io import BytesIO
from typing import List, Tuple, Optional

import discord

from pluralkit.bot import PluralKitBot, utils
from pluralkit.db import Database, ProxyMember, DatabaseConnection, MessageInfo


class NoWebhookPermission(Exception): pass


class NoDeletePermission(Exception): pass


class ProxyModule:
    bot: PluralKitBot
    db: Database
    logger: logging.Logger

    def __init__(self, bot, db):
        self.logger = logging.getLogger("pluralkit.proxy")
        self.bot = bot
        self.db = db

    async def get_webhook(self, conn: DatabaseConnection, channel: discord.TextChannel) -> discord.Webhook:
        try:
            # Check the DB for a webhook registered to this channel
            hook_data = await conn.get_webhook(channel.id)
            if hook_data:
                hook_id, hook_token = hook_data

                # Monkey-patching to fix a bug in the library, see https://github.com/Rapptz/discord.py/issues/1242
                adapter = discord.AsyncWebhookAdapter(self.bot.http._session)
                adapter.store_user = adapter._store_user
                return discord.Webhook.partial(hook_id, hook_token,
                                               adapter=adapter)

            # Okay, we didn't find one. Let's check the hook list for an existing one we haven't registered
            channel_webhooks: List[discord.Webhook] = await channel.webhooks()

            suitable_webhooks = [hook for hook in channel_webhooks if
                                 hook.user.id == self.bot.user.id and hook.name == "PluralKit Proxy Webhook"]
            if suitable_webhooks:
                hook = suitable_webhooks[0]

                # Let's also add this to the database, since it wasn't there before, apparently.
                await conn.add_webhook(channel.id, hook.id, hook.token)

                return hook

            # No hook there, either... time to create one.
            hook = await channel.create_webhook(name="PluralKit Proxy Webhook")

            # Add this to the DB, and return
            await conn.add_webhook(channel.id, hook.id, hook.token)
            return hook
        except discord.Forbidden:
            # Everything we do above is webhook-related, so this error must be because we have no webhook permissions
            raise NoWebhookPermission()

    async def send_proxy_message(self, conn: DatabaseConnection, channel: discord.TextChannel, member: ProxyMember,
                                 original_message: discord.Message, text: str):
        hook = await self.get_webhook(conn, channel)

        file = None
        if original_message.attachments:
            bio = BytesIO()
            await original_message.attachments[0].save(bio)
            file = discord.File(bio, original_message.attachments[0].filename)

        if not text and not file:
            # Don't bother with messages with no content AND no file
            return

        # Send the actual message
        message = await hook.send(username=member.full_name(), avatar_url=member.avatar_url, content=text, file=file,
                                  wait=True)

        # And save it in the database
        await conn.add_message(message.id, channel.id, member.id, original_message.author.id, text)

        # Plus, broadcast a message to the rest of the bot (eg. for logging)
        self.bot.dispatch("message_proxied", message, member)

    async def on_message(self, message: discord.Message):
        # Ignore messages from bots
        if message.author.bot:
            return

        # Ignore messages in DMs
        if not isinstance(message.channel, discord.TextChannel):
            return

        async with self.db.get() as conn:
            # Look up the sender in the DB, get a list of all their system members
            members = await conn.get_members_by_account(message.author.id)

            # Match the message and find a corresponding member with the included proxy tags
            match = self.match_proxy_tags(members, message.content)

            if match:
                # If we found a match, send the message
                member, proxy_text = match
                await self.send_proxy_message(conn, message.channel, member, message, proxy_text)

                # And then delete the original message
                try:
                    # We use the raw call for the Audit Log reason
                    await self.bot.http.delete_message(message.channel.id, message.id, reason="PluralKit: Deleted proxy trigger")
                except discord.Forbidden:
                    raise NoDeletePermission()

    def extract_leading_mentions(self, message_text: str) -> Tuple[str, str]:
        # This regex matches one or more mentions at the start of a message, separated by any amount of spaces
        match = re.match(r"^(<(@|@!|#|@&|a?:\w+:)\d+>\s*)+", message_text)
        if not match:
            return message_text, ""

        # Return the text after the mentions, and the mentions themselves
        return message_text[match.span(0)[1]:].strip(), match.group(0)

    def match_member_proxy_tags(self, member: ProxyMember, message_text: str) -> Optional[str]:
        # Skip members with no defined proxy tags
        if not member.prefix and not member.suffix:
            return None

        # DB defines empty prefix/suffixes as None, replace with empty strings to prevent errors
        prefix = member.prefix or ""
        suffix = member.suffix or ""

        # Ignore mentions at the very start of the message, and match proxy tags after those
        message_text, leading_mentions = self.extract_leading_mentions(message_text)

        self.logger.debug(
            "Matching text '{}' and leading mentions '{}' to proxy tags {}text{}".format(message_text, leading_mentions,
                                                                                         prefix, suffix))

        if message_text.startswith(member.prefix or "") and message_text.endswith(member.suffix or ""):
            prefix_length = len(prefix)
            suffix_length = len(suffix)

            # If suffix_length is 0, the last bit of the slice will be "-0", and the slice will fail
            if suffix_length > 0:
                inner_string = message_text[prefix_length:-suffix_length]
            else:
                inner_string = message_text[prefix_length:]

            # Add the mentions we stripped back
            inner_string = leading_mentions + inner_string
            return inner_string

    def match_proxy_tags(self, members: List[ProxyMember], message_text: str) -> Optional[Tuple[ProxyMember, str]]:
        # Sort by specificity (members with both prefix and suffix go higher)
        # This will make sure more "precise" proxy tags get tried first
        members: List[ProxyMember] = sorted(members, key=lambda x: int(
            bool(x.prefix)) + int(bool(x.suffix)), reverse=True)

        for member in members:
            match = self.match_member_proxy_tags(member, message_text)
            if match is not None:  # Using "is not None" because an empty string is OK here too
                self.logger.debug("Matched member {} with inner text '{}'".format(member.hid, match))
                return member, match


class ProxyDeletionModule:
    bot: PluralKitBot
    db: Database
    logger: logging.Logger

    def __init__(self, bot, db):
        self.logger = logging.getLogger("pluralkit.proxy")
        self.bot = bot
        self.db = db

    async def handle_delete(self, conn: DatabaseConnection, message: MessageInfo):
        # Delete it from the database
        await conn.delete_message(message.mid)

        # And fire a bot event (eg. for logging)
        self.bot.dispatch("proxy_message_deleted", message)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.emoji.name == "❌":
            async with self.db.get() as conn:
                msg = await conn.get_message_by_sender_and_id(payload.message_id, payload.user_id)
                if msg:
                    await self.handle_delete(conn, msg)

                    # Also delete the message, since this is just a reaction add
                    # Using the raw call here because we don't actually have a Message object
                    await self.bot.http.delete_message(payload.channel_id, payload.message_id,
                                                       reason="PluralKit: Deleted by reaction")

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        async with self.db.get() as conn:
            msg = await conn.get_message(payload.message_id)
            if msg:
                await self.handle_delete(conn, msg)

    async def on_raw_bulk_message_delete(self, payload: discord.RawBulkMessageDeleteEvent):
        async with self.db.get() as conn:
            for message_id in payload.message_ids:
                msg = await conn.get_message(message_id)
                if msg:
                    await self.handle_delete(conn, msg)