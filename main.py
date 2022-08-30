from discord.ext import commands
from discord import Intents
from discord.utils import get
from discord import FFmpegPCMAudio, AudioSource
from pydub import AudioSegment, effects
from threading import Thread
from math import ceil
import audioop
import logging
import youtube_dl
import os
from asyncio import sleep
from time import time

TOKEN = os.environ['TOKEN']
COOKIE = "cookies.txt"
bad_words = ['архипиздрит', 'пиздец', 'басран', 'драчун', 'дрочун', 'дрочу', 'дрочи', 'драчу', 'драчи', 'бздение', 'бздеть', 'бздех', 'бзднуть', 'бздун', 'бздунья', 'блять', 'бздюха', 'бикса', 'блежник', 'блудилище', 'бляд', 'блябу', 'блябуду', 'блядун', 'блядунья', 'блядь', 'блядюга', 'взьебка', 'волосянка', 'взьебывать', 'взъебывать', 'взебывать', 'выблядок', 'выблядыш', 'выебать', 'выеть', 'выпердеть', 'высраться', 'выссаться', 'говенка', 'говенный', 'говешка', 'говназия', 'говнецо', 'говно', 'говноед', 'говночист', 'говнюк', 'говнюха', 'говнядина', 'говняк', 'говняный', 'говнять', 'гондон', 'дермо', 'дерьмо', 'долбоеб', 'дрисня', 'дрист', 'дристать', 'дристануть', 'дристун', 'дристуха', 'дрочена', 'дрочила', 'дрочилка', 'дрочить', 'дрочка', 'ебало', 'ебальник', 'ебануть', 'ебаный', 'ебарь', 'ебатория', 'ебать', 'ебаться', 'ебались', 'ебец', 'ебливый', 'ебля', 'ебнуть', 'ебнуться', 'ебня', 'ебун', 'елда', 'елдак', 'елдачить', 'заговнять', 'задристать', 'задрока', 'заеба', 'заебанец', 'заебать', 'заебаться', 'заебываться', 'заеть', 'залупа', 'залупаться', 'залупить', 'залупиться', 'замудохаться', 'засерун', 'засеря', 'засерать', 'засирать', 'засранец', 'засрун', 'захуячить', 'злоебучий', 'изговнять', 'изговняться', 'кляпыжиться', 'курва', 'курвенок', 'курвин', 'курвяжник', 'курвяжница', 'курвяжный', 'манда', 'мандавошка', 'мандей', 'мандеть', 'мандища', 'мандюк', 'минет', 'минетчик', 'минетчица', 'мокрохвостка', 'мокрощелка', 'мудак', 'муде', 'мудеть', 'мудила', 'мудистый', 'мудня', 'мудоеб', 'мудозвон', 'муйня', 'набздеть', 'наговнять', 'надристать', 'надрочить', 'наебать', 'наебнуться', 'наебывать', 'нассать', 'нахезать', 'нахуйник', 'насцать', 'обдристаться', 'обдристайся', 'обосранец', 'порно', 'обосрать', 'обосцать', 'обосцаться', 'обсирать', 'опизде', 'отпиздячить', 'отпороть', 'отъеть', 'охуевательский', 'охуевать', 'охуевающий', 'охуеть', 'охуительный', 'охуячивать', 'охуячить', 'педрик', 'пердеж', 'пердение', 'пердеть', 'пердильник', 'перднуть', 'пердун', 'пердунец', 'пердунина', 'пердунья', 'пердуха', 'пердь', 'передок', 'пернуть', 'пидор', 'пизда', 'пиздануть', 'пизденка', 'пиздеть', 'пиздить', 'пиздища', 'пиздобратия', 'пиздоватый', 'пиздорванец', 'пиздорванка', 'пиздострадатель', 'пиздун', 'пиздюга', 'пиздюк', 'пиздячить', 'писять', 'питишка', 'плеха', 'подговнять', 'подъебнуться', 'поебать', 'поеть', 'попысать', 'посрать', 'поставить', 'поцоватый', 'презерватив', 'проблядь', 'проебать', 'промандеть', 'промудеть', 'пропиздеть', 'пропиздячить', 'пысать', 'разъеба', 'разъебай', 'распиздай', 'распиздеться', 'распиздяй', 'распроеть', 'растыка', 'сговнять', 'секель', 'серун', 'серька', 'сика', 'сикать', 'сикель', 'сирать', 'сирывать', 'скурвиться', 'скуреха', 'скурея', 'скуряга', 'скуряжничать', 'спиздить', 'срака', 'сраный', 'сранье', 'срать', 'срун', 'ссака', 'ссаки', 'ссать', 'старпер', 'струк', 'суходрочка', 'сцавинье', 'сцака', 'сцаки', 'сцание', 'сцать', 'сциха', 'сцуль', 'сцыха', 'сыкун', 'титечка', 'титечный', 'титка', 'титочка', 'титька', 'трипер', 'триппер', 'уеть', 'усраться', 'усцаться', 'фик', 'фуй', 'хезать', 'хер', 'херня', 'херовина', 'херовый', 'хитрожопый', 'хлюха', 'хуевина', 'хуевый', 'хуек', 'хуепромышленник', 'хуерик', 'хуесос', 'хуище', 'хуй', 'хуйня', 'хуйрик', 'хуякать', 'хуякнуть', 'целка', 'шлюха']
replace_list = {'c': 'с', 'o': 'о', 'e': 'е', 'u': 'и', 'a': 'а', 'bl': 'ы', 'bi': 'ы', 'y': 'у', 'p': 'р', 'x': 'х', 'b': 'в'}

YDL_OPTIONS = {'format': "bestaudio/best[asr=48000]",
			   'noplaylist': 'True',
			   'cookiefile': COOKIE,
			   'quiet': 'True'}

YDL2_OPTIONS = {'format': "bestvideo/best",
			   'noplaylist': 'True',
			   'cookiefile': COOKIE,
			   'quiet': 'True'}


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
	intents = Intents.default()
	intents.members = True
	bot = commands.Bot(command_prefix=('!', '/', '?'), case_insensitive=True, intents=intents)
	delay_time = {}

	@bot.command()
	async def sanya_negr(ctx, arg=None):
		await ctx.send("как там твои папа и папа?")

	@bot.command(aliases=['pa', 'pau', 'з', 'зфгыу'])
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

	@bot.command(aliases=['r', 'res', 'к', 'куыгьу'])
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

	@bot.command(aliases=['s', 'sk', 'ы', 'ылшз'])
	async def skip(ctx):
		if is_in_channel(ctx.message.author.voice):
			voice = get_voice_attr(ctx)
			if not voice:
				await ctx.send("Бот не зашёл в канал")
				return
			if not voice.is_playing():
				await ctx.send("Музыка не играет.")
				return
			voice.source.is_skip = True
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
		try:
			if not voice:
				voice = await channel.connect()
			elif voice and not voice.is_connected():
				await voice.connect(reconnect=True, timeout=10.0)
				await voice.move_to(channel)
		except:
			return False
		await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
		return voice

	async def play_audio(ctx, url):
		voice = await get_voice(ctx)
		if voice is False:
			await ctx.send("еблан, колонка не видит твой канал! дай прав")
			return False
		if voice.is_playing():
			if not voice.source.is_queue:
				voice.stop()
			else:
				if url in voice.source.audio_queue:
					return False
				voice.source.audio_queue.append(url)
				return True

		voice.play(URLPCMTransformer(url))
		return voice

	class URLPCMTransformer(AudioSource):
		def __init__(self, url, volume=1.0, normalize=False, bass_volume=0.0, loop=False):
			self.url = url
			self.audio_source = CachedFFmpegPCMAudio(url)

			self.loop = loop
			self._volume = volume
			self._bass_volume = bass_volume
			self.normalize = normalize
			self.is_queue = False
			self.audio_queue = [self.url]
			self.audio_index = 0
			self.is_skip = False

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
			f_data = sample.low_pass_filter(500)
			filtered = audioop.mul(f_data.raw_data, 2, self._bass_volume)
			return audioop.add(raw_sample, filtered, 2)

		def effect_volume(self, ret):
			return audioop.mul(ret, 2, min(self._volume, 2.0))

		def effect_normalize(self, ret):
			sample = AudioSegment(data=ret, sample_width=2, frame_rate=48000, channels=2)
			return effects.normalize(sample).raw_data

		def loop_read(self):
			ret = self.audio_source.read()
			if ret == b'' or self.is_skip:
				self.audio_index += 1
				is_queue_end = self.audio_index >= len(self.audio_queue)
				if (self.loop or not is_queue_end) and not self.is_skip and self.url is not None:
					if self.loop and is_queue_end:
						self.audio_index = 0
					self.url = self.audio_queue[self.audio_index]
					self.audio_source = CachedFFmpegPCMAudio(self.url)
					return self.audio_source.read()
				else:
					self.is_skip = False
					self.url = None
					return b''
			else:
				return ret

		def read(self):
			ret = self.loop_read()
			if ret == b'' or self.url is None:
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
			except IndexError:
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


	@bot.command(aliases=['n', 'norm', 'т', 'тщкьфдшяу'])
	async def normalize(ctx, arg=None):
		if not is_in_channel(ctx.message.author.voice):
			await ctx.send("Вы не подключены к каналу")
			return
		channel = ctx.message.author.voice.channel
		voice = get_voice_attr(ctx)
		if not voice:
			await ctx.send("Бот не зашёл в анал")
			return
		if channel and voice.is_playing():
			voice.source.is_queue = not voice.source.is_queue
		else:
			await ctx.send("Вы не подключены к каналу")

	@bot.command(aliases=['q', 'й', 'йгугу'])
	async def queue(ctx, arg=None):
		if not is_in_channel(ctx.message.author.voice):
			await ctx.send("Вы не подключены к каналу")
			return
		channel = ctx.message.author.voice.channel
		voice = get_voice_attr(ctx)
		if not voice:
			await ctx.send("Бот не зашёл в анал")
			return
		if not ctx.message.author.guild_permissions.administrator and ctx.message.author.id != 252788456248442880:
			await ctx.send("Недостаточно прав!")
			return
		if channel and voice.is_playing():
			voice.source.is_queue = not voice.source.is_queue
			voice.source.loop = False
			if voice.source.is_queue:
				await ctx.send("Очередь треков включена!")
			else:
				await ctx.send("Очередь треков была отключена!")
				voice.source.audio_queue = []
		else:
			await ctx.send("Вы не подключены к каналу")

	@bot.command(aliases=['b', 'bs', 'ифыыищщые', 'и', 'иы'])
	async def bassboost(ctx, arg=None):
		if arg != None:
			volume = False
			try:
				volume = float(arg)
			except ValueError:
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


	@bot.command(aliases=['vol', 'v', 'мщдгьу', 'мщд', 'м'])
	async def volume(ctx, arg=None):
		if arg != None:
			volume = False
			try:
				volume = float(arg)
			except ValueError:
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

	@bot.command(aliases=['l', 'lp', 'дщщз', 'д', 'дз'])
	async def loop(ctx, arg=None):
		if not is_in_channel(ctx.message.author.voice):
			await ctx.send("Вы не подключены к каналу")
			return
		channel = ctx.message.author.voice.channel
		voice = get_voice_attr(ctx)
		if not voice:
			await ctx.send("Бот не зашёл в анал или трек не играет")
			return
		if not voice.is_playing():
			await ctx.send("Трек не играет")
			return
		if channel:
			if voice.source.is_queue and (not ctx.message.author.guild_permissions.administrator and ctx.message.author.id != 252788456248442880):
				await ctx.send("Недостаточно прав!")
				return
			voice.source.loop = not voice.source.loop
			if voice.source.loop:
				await ctx.send("Зацикливание для текущего трека включено")
			else:
				await ctx.send("Зацикливание для текущего трека выключено")
		else:
			await ctx.send("Вы не подключены к каналу")

	def replace_on_normal(txt):
		for word in replace_list:
			txt = txt.replace(word, replace_list[word].lower())
			txt = txt.replace(word, replace_list[word].upper())
		return txt

	def remove_bad_words(txt):
		new_txt1 = replace_on_normal(txt.lower())
		for word in bad_words:
			if word not in new_txt1.lower().replace(' ', ''):
				continue
			word_length = len(word)
			first_letter = word[0]
			for i in range(len(txt)):
				if new_txt1[i].lower() != first_letter:
					continue
				min_length = word_length
				checking_text = new_txt1[i:i+min_length].lower()
				while (' ' in checking_text) or ('\n' in checking_text):
					min_length += 1
					checking_text = new_txt1[i:i+min_length].lower().replace(' ', '').replace('\n', '')
				if checking_text == word:
					txt = txt[:i] + '#' * min_length + txt[i+min_length:]
		return txt

	@bot.command(aliases=['gl', 'g_l', 'get_l', 'пуе_дштл', 'пд', 'п_д', 'пуе_д'])
	async def get_link(ctx, *args):
		arg = ' '.join(args)
		meta = None
		try:
			with youtube_dl.YoutubeDL(YDL2_OPTIONS) as ydl2:
				meta = ydl2.extract_info("ytsearch:" + arg, download=False)
		except:
			await ctx.send("Не удалось скачать видео (18+, слишком много запросов или видео не доступно в стране сервера бота)")
			return
		entries = meta['entries']
		if len(entries) <= 0:
			await ctx.send("Не было найдено ни одного видео по такому запросу")
			return
		await ctx.send("Найдено видео: " + remove_bad_words(str(entries[0]['title']).replace('*', '')) + ". Ссылка на него для скачивания: <" + str(entries[0]['formats'][-1]['url']) + ">")

	@bot.command(aliases=['p', 'pl', 'з', 'зд', 'здфй'])
	async def play(ctx, *args):
		guild_id = ctx.guild.id
		if guild_id in delay_time:
			if time() - delay_time[guild_id] < 15:
				await ctx.send("Не надо так...")
				return
		delay_time[guild_id] = time()
	
			
		if len(args) == 0:
			await ctx.send("Вы не указали, какой видос вам включать или дали неправильную ссылку")
			return

		if not is_in_channel(ctx.message.author.voice):
			await ctx.send("Вы не подключены к каналу")
			return

		voice_channel_perms = ctx.message.author.voice.channel.permissions_for(guild_vitya[ctx.guild.id])
		text_channel_perms = ctx.message.channel.permissions_for(guild_vitya[ctx.guild.id])
		if not voice_channel_perms.connect or not voice_channel_perms.speak:
			await ctx.send("еблан, колонка не видит твой канал! дай прав")
			return
		if not text_channel_perms.read_messages:
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

		async def try_play(tries=0):
			voice = None
			try:
				voice = await play_audio(ctx, entries[0]['formats'][tries]['url'])
				if type(voice) is bool:
					return voice
			except:
				pass
			if not hasattr(voice, 'is_playing') or not voice.is_playing():
				await sleep(5)
				if tries > 3:
					return False
				return await try_play(tries=tries+1)
			return True
		if await try_play():
			await ctx.send("Добавлено видео: " + remove_bad_words(str(entries[0]['title']).replace('*', '')) + ". <" + str(entries[0]['webpage_url']) + ">")
			print(f"Added video {str(entries[0]['title'])}. {str(entries[0]['webpage_url'])} in guild: {ctx.guild.id}, {ctx.guild.name}")
		else:
			await ctx.send("Не удалось добавить видео!")

	bot.run(TOKEN)
