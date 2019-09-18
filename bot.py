import discord
from discord.ext.commands import Bot
from datetime import datetime
import asyncio
import zmq
import zmq.asyncio
import json
import websockets
import os
from pytz import timezone

from src.user_command import UserCommand
from src.smart_message import smart_message
from src.config import get_session
from src.models import Command

starboarded_messages = []


class CoolBot(Bot):

    def __init__(self, **kwargs):
        self.user_commands = {}
        self.session = get_session()
        self.guild_counter = (0, 0)
        self.tracked_messages = {}
        self.deletable_messages = []
        super().__init__(**kwargs)

    def run(self, token, q=None):
        self.q = q

        ctx = zmq.asyncio.Context()
        self.loop.create_task(self.poll_requests(ctx))
        super().run(token)

    async def on_ready(self):
        await self.initialize_user_commands()
        print('Logged on as {0}!'.format(self.user))

    async def initialize_user_commands(self):
        command_list = ()
        for guild in self.guilds:
            self.user_commands.setdefault(int(guild.id), [])
        for command in command_list:
            self.user_commands.setdefault(command.server_id, [])
            self.user_commands[command.server_id].append(UserCommand(
                self.session,
                self,
                command.trigger.replace(str(command.server_id), '', 1),
                command.response, command.count,
                self.get_guild(command.server_id),
                command.author_id))
        for guild, cmds in self.user_commands.items():
            self.user_commands[guild].sort()

BOT_PREFIX = ("?", "!")
coolbot = CoolBot(command_prefix=BOT_PREFIX)

coolbot.load_extension(f"src.ext.events_cog")
coolbot.load_extension(f"src.ext.set_cog")
coolbot.load_extension('src.api.api')

if __name__ == '__main__':
    from src.config import secret_token
    coolbot.run(secret_token)
