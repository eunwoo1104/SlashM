import os
import logging
import discord
from modules import SMClient

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)  # DEBUG/INFO/WARNING/ERROR/CRITICAL
handler = logging.FileHandler(filename=f'slashm.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = SMClient(command_prefix="sm!",
               allowed_mentions=discord.AllowedMentions(everyone=False),
               intents=discord.Intents.all())

[bot.load_extension("cogs." + x.replace(".py", "")) for x in os.listdir("cogs") if x.endswith(".py")]

bot.run()
