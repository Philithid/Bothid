# bothid.py
# GENERAL
import os
import logging
from datetime import datetime

# PRIVATE
from utils import config_loader

# DISCORD
# from discord
from discord.ext import commands

# SQL
import asyncio
import aiomysql

from dotenv import load_dotenv

load_dotenv()


class Bothid(commands.Bot):

    def __init__(self, *args, **kwargs):
        sql_cursor = None
        sql_db = None
        super().__init__(*args, **kwargs)
        self.log = self.create_logger(f'LOG_{datetime.now().date()}')
        self.log.info(f'Bot is starting..')
        self.load_modules()

    """ SQL """

    async def init_db(self, loop):
        self.sql_db = await aiomysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PWD'),
            db=os.getenv('DB_NAME'),
            loop=loop,
            autocommit=True
        )
        self.log.debug(f'Database connection established')
        self.sql_cursor = await self.sql_db.cursor()
        await self.sql_execute(
            f'CREATE TABLE IF NOT EXISTS guilds (id BIGINT UNSIGNED PRIMARY KEY, name VARCHAR(255) NOT NULL );'
        )
        self.log.debug(f'Database initialized')

    async def sql_execute(self, query: str):
        await self.sql_cursor.execute(query)
        self.log.debug(f'SQL Query executed: {query}')

    async def sql_fetchall(self, query: str):
        await self.sql_execute(query)
        return await self.sql_cursor.fetchall()

    async def sql_fetchmany(self, query: str, rows: int):
        await self.sql_execute(query)
        sql_res = None
        if rows == 1:
            sql_res = await self.sql_cursor.fetchone()
        elif rows > 1:
            sql_res = await self.sql_cursor.fetchmany(rows)
        return sql_res

    """ OTHER """

    @commands.Cog.listener()
    async def on_ready(self):
        await self.init_db(self.loop)
        self.log.info(f'Bot started')

    def reload_modules(self):
        for name in config_loader.load_conf("config"):
            try:
                self.reload_extension(f'modules.{name}')
                self.log.debug(f'{name} module loaded')
            except commands.ExtensionNotFound:
                self.log.error(f'could not load {name}')

    def load_modules(self):
        for name in config_loader.load_conf("config"):
            try:
                self.load_extension(f'modules.{name}')
                self.log.debug(f'{name} module loaded')
            except commands.ExtensionNotFound:
                self.log.error(f'could not load {name}')

    @staticmethod
    def create_logger(file: str):
        logger = logging.getLogger(file)
        logger.setLevel(logging.DEBUG)
        path = f"logs/{file}.log"
        handler = logging.FileHandler(filename=path, encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(handler)
        return logger


bot = Bothid(command_prefix='!', owner_id=142622339434151936)

bot.run(os.getenv('DISCORD_TOKEN'))
