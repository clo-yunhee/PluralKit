import logging

import discord
from discord.ext.commands import Bot

from pluralkit.db import Database


class PluralKitBot(Bot):
    logger: logging.Logger
    db: Database

    def __init__(self, db: Database):
        super().__init__(command_prefix="pk;")

        self.logger = logging.getLogger("pluralkit.bot")
        self.db = db

        self.logger.info("Initializing bot...")
        self.logger.info("discord.py version {}.{}.{}-{}{}".format(
            discord.version_info.major,
            discord.version_info.minor,
            discord.version_info.micro,
            discord.version_info.releaselevel,
            discord.version_info.serial
        ))

        from pluralkit.bot.proxy import ProxyModule, ProxyDeletionModule
        from pluralkit.bot.log import LoggerModule
        from pluralkit.bot.commands.system import SystemCommands

        self.add_cog(ProxyModule(self, db))
        self.add_cog(ProxyDeletionModule(self, db))
        self.add_cog(LoggerModule())

        self.add_cog(SystemCommands(self))

        self.before_invoke(self.setup_conn_db)
        self.after_invoke(self.release_conn_db)

    async def on_ready(self):
        self.logger.info("Logged in.")
        self.logger.info("- User: {}#{}".format(self.user.name, self.user.discriminator))
        self.logger.info("- Guilds: {}".format(len(self.guilds)))

    async def setup_conn_db(self, ctx):
        conn = await self.db.get_raw()
        ctx.conn = conn

    async def release_conn_db(self, ctx):
        await self.db.release_raw(ctx.conn)
