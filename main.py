from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio, AudioSource
from pydub import AudioSegment, effects
from threading import Thread
from time import time
from math import ceil
import audioop
import logging
import youtube_dl
import os

TOKEN = os.environ['TOKEN']
COOKIE = "cookies.txt"

YDL_OPTIONS = {'format': "bestaudio/best[asr=48000]",
               'noplaylist': 'True',
               'cookiefile': COOKIE,
               'quiet': 'True'}

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
    bot = commands.Bot(command_prefix="!")

    @bot.command(aliases=['pa', 'pau', 'PA', 'PAU'])
    async def pause(ctx):
        if not is_in_channel(ctx.message.author.voice):
            await ctx.send("Вы не подключены к каналу")
            return
        voice = get_voice_attr(ctx)
        if not voice:
            await ctx.send("Бот не зашёл в канал")
            return
        if not voice.is_playing():
            await ctx.send("У вас не играет трек")
            return
        voice.pause()


    @bot.event
    async def on_ready():
        print("Bot is working!")

    @bot.command(aliases=['r', 'res', 'R', 'RES', 'RESUME'])
    async def resume(ctx):
        if not is_in_channel(ctx.message.author.voice):
            await ctx.send("Вы не подключены к каналу")
            return
        voice = get_voice_attr(ctx)
        if not voice:
            await ctx.send("Бот не зашёл в канал")
            return
        if voice.is_playing():
            await ctx.send("У итак играет трек")
            return
        voice.resume()

    @bot.command(aliases=['s', 'sk', 'S', 'SK', 'SKIP'])
    async def skip(ctx):
        if ctx.message.author.voice.channel:
            voice = get_voice_attr(ctx)
            if not voice:
                await ctx.send("Бот не зашёл в канал")
                return
            if not voice.is_playing():
                await ctx.send("Музыка не играет.")
                return
            voice.stop()
        else:
            await ctx.send("Вы не подключены к каналу.")

    def is_in_channel(state):
        if state is None:
            return False
        return True

    def get_voice_attr(ctx):
        voice = get(bot.voice_clients, guild=ctx.guild)
        return voice if voice else False

    async def get_voice(ctx):
        channel = ctx.message.author.voice.channel
        voice = get_voice_attr(ctx)
        if not voice:
            voice = await channel.connect()
        elif voice and not voice.is_connected():
            await voice.connect(reconnect=True, timeout=1.0)
            await voice.move_to(channel)
        await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
        return voice

    async def play_audio(ctx, url):
        voice = await get_voice(ctx)
        if voice.is_playing():
            voice.stop()

        voice.play(URLPCMTransformer(url))
        return True

    class URLPCMTransformer(AudioSource):
        def __init__(self, url, volume=1.0, normalize=False, bass_volume=0.0, loop=False):
            self.url = url
            self.audio_source = CachedFFmpegPCMAudio(url)

            self.loop = loop
            self._volume = volume
            self._bass_volume = bass_volume
            self.normalize = normalize

        @property
        def bass_volume(self):
            return self._bass_volume

        @bass_volume.setter
        def bass_volume(self, value):
            self._bass_volume = max(value, 0.0)

        @property
        def volume(self):
            return self._volume

        @volume.setter
        def volume(self, value):
            self._volume = max(value, 0.0)

        def effect_bassboost(self, ret):
            sample = AudioSegment(data=ret, sample_width=2, frame_rate=48000, channels=2)
            raw_sample = sample.raw_data
            filtered = audioop.mul(sample.low_pass_filter(500).raw_data, 2, self._bass_volume)
            return audioop.add(raw_sample, filtered, 2)

        def effect_volume(self, ret):
            return audioop.mul(ret, 2, min(self._volume, 2.0))

        def effect_normalize(self, ret):
            sample = AudioSegment(data=ret, sample_width=2, frame_rate=48000, channels=2)
            return effects.normalize(sample).raw_data

        def loop_read(self):
            ret = self.audio_source.read()
            if ret == b'':
                if self.loop:
                    self.audio_source = CachedFFmpegPCMAudio(self.url)
                    return self.audio_source.read()
                else:
                    return b''
            else:
                return ret

        def read(self):
            ret = self.loop_read()
            if ret == b'':
                return b''
            if self.normalize:
                ret = self.effect_normalize(ret)
            if self._bass_volume > 0:
                ret = self.effect_bassboost(ret)
            if self._volume != 1:
                ret = self.effect_volume(ret)
            return ret

        def cleanup(self) -> None:
            self.audio_source.cleanup()


    class CachedFFmpegPCMAudio(FFmpegPCMAudio):
        cache_times = 250
        cache = []
        futures = []
        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}

        def __init__(self, source):
            super().__init__(source, **self.FFMPEG_OPTS)
            self.cache_times = 250
            self.cache = []
            self.futures = []

        def append_to_cache(self):
            super_read = super().read()
            if super_read != b'':
                self.cache.append(super_read)
                return True
            else:
                return False

        def read(self):
            cache_len = len(self.cache)
            if cache_len == 0:
                self.append_to_cache()
                for i in range(self.cache_times):
                    if not self.append_to_cache():
                        break

            first = None
            try:
                first = self.cache[0]
            except:
                return b''
            del self.cache[0]
            running_futures = []
            for gun in self.futures:
                if gun.is_alive():
                    running_futures.append(gun)
            self.futures = running_futures

            if len(running_futures) < (self.cache_times - 3):
                future = Thread(target=self.append_to_cache, daemon=True)
                future.start()
                self.futures.append(future)
            else:
                result_sum = 0
                futures_size = len(running_futures)
                for i in range(futures_size):
                    gun = running_futures[i]
                    time_before = time()
                    while gun.is_alive():
                        pass
                    time_after = time()
                    result_sum += (time_after - time_before) / 0.015
                self.cache_times = min(ceil(result_sum / futures_size) + 10, 1500)

            return first


    @bot.command(aliases=['n', 'N', 'norm', 'NORM', 'NORMALIZE'])
    async def normalize(ctx, arg=None):
        channel = ctx.message.author.voice.channel
        voice = get_voice_attr(ctx)
        if not voice:
            await ctx.send("Бот не зашёл в анал")
            return
        if channel and voice.is_playing():
            voice.source.normalize = not voice.source.normalize
        else:
            await ctx.send("Вы не подключены к каналу")

    @bot.command(aliases=['b', 'bs', 'B', 'BS', 'BASSBOOST'])
    async def bassboost(ctx, arg=None):
        if arg != None:
            volume = False
            try:
                volume = float(arg)
            except:
                await ctx.send("Неверное значение")
                return
            channel = ctx.message.author.voice.channel
            voice = get_voice_attr(ctx)
            if not voice:
                await ctx.send("Бот не зашёл в анал")
                return
            if volume > 1000:
                await ctx.send("Слишком большое значение")
                return
            if channel and voice.is_playing():
                voice.source.bass_volume = volume
            else:
                await ctx.send("Вы не подключены к каналу")
        else:
            await ctx.send("Вы не указали аргумент")


    @bot.command(aliases=['vol', 'v', 'VOL', 'V', 'VOLUME'])
    async def volume(ctx, arg=None):
        if arg != None:
            volume = False
            try:
                volume = float(arg)
            except:
                await ctx.send("Неверное значение")
            channel = ctx.message.author.voice.channel
            voice = get_voice_attr(ctx)
            if not voice:
                await ctx.send("Бот не зашёл в анал")
                return
            if volume > 1000:
                await ctx.send("Слишком большое значение")
                return
            if channel and voice.is_playing():
                voice.source.volume = volume
            else:
                await ctx.send("Вы не подключены к каналу")
        else:
            await ctx.send("Вы не указали аргумент")


    @bot.command(aliases=['l', 'lp', 'L', 'LP', 'LOOP'])
    async def loop(ctx, arg=None):
        channel = ctx.message.author.voice.channel
        voice = get_voice_attr(ctx)
        if not voice:
            await ctx.send("Бот не зашёл в анал или трек не играет")
            return
        if not voice.is_playing():
            await ctx.send("Трек не играет")
            return
        if channel:
            voice.source.loop = not voice.source.loop
            if voice.source.loop:
                await ctx.send("Зацикливание для текущего трека включено")
            else:
                await ctx.send("Зацикливание для текущего трека выключено")
        else:
            await ctx.send("Вы не подключены к каналу")

    @bot.command(aliases=['p', 'pl', 'P', 'PL', 'PLAY'])
    async def play(ctx, *args):
        if len(args) == 0:
            await ctx.send("Вы не указали, какой видос вам включать или дали неправильную ссылку")
            return

        if not is_in_channel(ctx.message.author.voice):
            await ctx.send("Вы не подключены к каналу")
            return

        arg = ' '.join(args)
        meta = None
        try:
            meta = ydl.extract_info("ytsearch:" + arg, download=False)
        except:
            await ctx.send("Не удалось скачать видео (18+, слишком много запросов или видео не доступно в стране сервера бота)")
            return
        entries = meta['entries']
        if len(entries) <= 0:
            await ctx.send("Не было найдено ни одного видео по такому запросу")
            return
        await play_audio(ctx, meta['entries'][0]['formats'][0]['url'])
        await ctx.send("Воспроизвожу видео: **" + entries[0]['title'] + "**")

    bot.run(TOKEN)
