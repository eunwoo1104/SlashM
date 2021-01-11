import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash import SlashCommandOptionType
from discord_slash.utils import manage_commands
from modules import SMClient

guild_ids = [796909646005796878]


class Music(commands.Cog):
    def __init__(self, bot: SMClient):
        self.bot = bot
        self.bot.slash.get_cog_commands(self)

    def cog_unload(self):
        self.bot.slash.remove_cog_commands(self)

    @commands.Cog.listener()
    async def on_socket_response(self, payload):
        return self.bot.discodo.discordDispatch(payload)

    async def voice_check(self, ctx: SlashContext, *, check_connected: bool = False, check_playing: bool = False, check_paused: bool = False) -> tuple:
        voice: discord.VoiceState = ctx.author.voice

        if check_playing and check_paused:
            return 5, "봇 소스코드에 문제가 있습니다."

        if not voice or not voice.channel:
            return 1, "먼저 음성 채널에 들어가주세요."

        codo = self.bot.discodo.getVC(ctx.guild.id, safe=True)

        if check_connected and codo is None:
            return 2, "먼저 음악을 재생해주세요."

        if check_playing and codo.paused:
            return 3, "음악이 재생중이 아닙니다. 먼저 음악을 재생해주세요."

        if check_paused and not codo.paused:
            return 4, "음악이 재생중입니다. 먼저 음악을 일시정지해주세요."

        return 0, None

    @cog_ext.cog_slash(name="player", description="현재 플레이어 정보를 보여줍니다.", guild_ids=guild_ids)
    async def player_info(self, ctx: SlashContext):
        codo = self.bot.discodo.getVC(ctx.guild.id, safe=True)
        if not codo:
            return await ctx.send(content="먼저 음악을 재생해주세요.", complete_hidden=True)
        await ctx.send(5)
        embed = discord.Embed(title=f"{ctx.guild.name} 서버 플레이어")
        #embed.add_field()
        await ctx.send(embeds=[embed])

    @cog_ext.cog_slash(name="play", description="음악을 재생합니다.",
                       options=[manage_commands.create_option("url-또는-제목", "유튜브 URL 또는 영상 제목입니다.", SlashCommandOptionType.STRING, True)],
                       guild_ids=guild_ids)
    async def play(self, ctx: SlashContext, url: str):
        check = await self.voice_check(ctx)
        if check[0] != 0:
            return await ctx.send(content=check[1], complete_hidden=True)
        await ctx.send(5)
        codo = self.bot.discodo.getVC(ctx.guild.id, safe=True)
        if not codo:
            await self.bot.connect_voice(ctx.guild, ctx.author.voice.channel)
            await ctx.send(content="음성 채널에 연결했어요! 잠시만 기다려주세요...") # Delays so vc can be created.
            codo = self.bot.discodo.getVC(ctx.guild.id, safe=True)
        try:
            is_playing = codo.state == "playing"
        except AttributeError: # This need to be fixed at discodo.
            is_playing = False
        codo.autoplay = False
        src = await codo.loadSource(url)
        if isinstance(src, list):
            return await ctx.send(content=f"재생목록의 영상 {len(src)}개가 추가되었어요!")
        else:
            return await ctx.send(content=f"{src.title}을(를) 대기열에 넣었어요!" if is_playing else f"{src.title}을(를) 재생할께요!")

    @cog_ext.cog_slash(name="skip", description="현재 재생중인 트랙을 스킵합니다.",
                       #options=[manage_commands.create_option("오프셋", "스킵할 트랙 번호입니다. 기본값은 1 입니다.", SlashCommandOptionType.INTEGER, False)],
                       guild_ids=guild_ids)
    async def skip(self, ctx: SlashContext, offset: int = 1):
        check = await self.voice_check(ctx)
        if check[0] != 0:
            return await ctx.send(content=check[1], complete_hidden=True)
        await ctx.send(5)
        codo = self.bot.discodo.getVC(ctx.guild.id, safe=True)
        codo.skip(offset)
        await ctx.send(content=f"`{offset}`번 트랙을 스킵했어요!" if offset > 1 else "현재 노래를 스킵했어요!")

    @cog_ext.cog_slash(name="volume", description="볼륨울 조절합니다.",
                       options=[manage_commands.create_option("볼륨값", "볼륨 값입니다. (1~100)", SlashCommandOptionType.INTEGER, True)],
                       guild_ids=guild_ids)
    async def volume(self, ctx: SlashContext, vol: int):
        check = await self.voice_check(ctx, check_playing=True, check_connected=True)
        if check[0] != 0:
            return await ctx.send(content=check[1], complete_hidden=True)
        if not 0 < vol <= 100:
            return await ctx.send(content="볼륨은 1~100 이어야 합니다.", complete_hidden=True)
        await ctx.send(5)
        codo = self.bot.discodo.getVC(ctx.guild.id, safe=True)
        codo.volume = vol/100
        await ctx.send(content=f"볼륨을 `{vol}`%로 조절했어요!")

    @cog_ext.cog_slash(name="shuffle", description="재생목록을 섞습니다.",
                       guild_ids=guild_ids)
    async def shuffle(self, ctx: SlashContext):
        check = await self.voice_check(ctx, check_connected=True)
        if check[0] != 0:
            return await ctx.send(content=check[1], complete_hidden=True)
        await ctx.send(5)
        codo = self.bot.discodo.getVC(ctx.guild.id, safe=True)
        codo.shuffle()
        await ctx.send(content="재생목록을 섞었어요!")

    @cog_ext.cog_slash(name="pause", description="플레이어를 일시정지합니다.",
                       guild_ids=guild_ids)
    async def pause(self, ctx: SlashContext):
        check = await self.voice_check(ctx, check_connected=True, check_playing=True)
        if check[0] != 0:
            return await ctx.send(content=check[1], complete_hidden=True)
        await ctx.send(5)
        codo = self.bot.discodo.getVC(ctx.guild.id, safe=True)
        codo.pause()
        await ctx.send(content="플레이어를 일시정지했어요!")

    @cog_ext.cog_slash(name="resume", description="플레이어를 일시정지를 해제합니다.",
                       guild_ids=guild_ids)
    async def resume(self, ctx: SlashContext):
        check = await self.voice_check(ctx, check_connected=True, check_paused=True)
        if check[0] != 0:
            return await ctx.send(content=check[1], complete_hidden=True)
        await ctx.send(5)
        codo = self.bot.discodo.getVC(ctx.guild.id, safe=True)
        codo.resume()
        await ctx.send(content="플레이어를 다시 재생할께요!")


def setup(bot):
    bot.add_cog(Music(bot))
