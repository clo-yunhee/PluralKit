import os
import logging

from pluralkit.bot.bot import PluralKitBot


async def run():
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")

    from pluralkit import db

    token = os.environ["TOKEN"]

    db_user = os.environ["DATABASE_USER"]
    db_pass = os.environ["DATABASE_PASS"]
    db_host = os.environ["DATABASE_HOST"]
    db_port = int(os.environ["DATABASE_PORT"])
    db_name = os.environ["DATABASE_NAME"]

    async with db.Database(user=db_user, password=db_pass, host=db_host, port=db_port, database=db_name) as db:
        bot = PluralKitBot(db)
        try:
            await bot.start(token)
        except KeyboardInterrupt:
            await bot.logout()