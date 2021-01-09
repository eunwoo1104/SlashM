import json
import discord
import discodo
from discord.ext import commands
from discord_slash import SlashCommand
from . import sqlite_db


class SMClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slash = SlashCommand(self, override_type=True, auto_register=True, auto_delete=True)
        self.db = sqlite_db.SQLiteDB("userdata")
        self.discodo = discodo.ClientManager() # Change to remote maybe.
        # self.add_listener(self.discodo_on_socket_response, "on_socket_response")

    async def discodo_on_socket_response(self, *args, **kwargs):
        return self.discodo.discordDispatch(*args, **kwargs)

    @staticmethod
    def get_setting(key: str):
        with open("bot_settings.json", "r") as f:
            return json.load(f).get(key)

    def run(self):
        super(SMClient, self).run(self.get_setting("stable_token" if not self.get_setting("debug") else "canary_token"))

    async def connect_voice(self, guild: discord.Guild, channel: discord.VoiceChannel = None):
        await self.ws.voice_state(guild.id, channel.id)

    async def disconnect_voice(self, guild: discord.Guild):
        # Does the same job as `connect_voice` without `channel` arg.
        await self.ws.voice_state(guild.id, None)
