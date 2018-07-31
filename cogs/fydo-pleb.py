from discord.ext import commands
from discord.ext.commands import bot
import discord
import json
import asyncio
import os.path
import re
import datetime

class arange:
	def __init__(self, n):
		self.n = n
		self.i = 0
	async def __aiter__(self):
		return self
	async def __anext__(self):
		i = self.i
		self.i += 1
		if self.i <= self.n:
			await asyncio.sleep(0)  # insert yield point
			return i
		else:
			raise StopAsyncIteration

class FydoTranslate:
	#########################
	#  Default Values Here  #
	#########################
	def __init__(self, bot):
		self.bot = bot

		self.initialised = False
		self.description = "Translation for whatever the hell Fyd0 just said"
		self.icon = "https://cdn.discordapp.com/avatars/456691275178049558/a9b4641d2469f9cb6da79846c8c9d503.png?size=256"
		self.filename = "FydoDictionary.txt"
		self.translateids = [241008111605907456]
		self.logfile = "FydoLog.txt"
		self.fydowords = {}

	#########################
	#	Actual Functions	#
	#########################
	async def addWord(self, fydoword, englishwords):
		lowerword = fydoword.lower()
		if lowerword not in self.fydowords:
			self.fydowords[lowerword] = []
		key = str(self.fydowords[lowerword])
		prevalue = list(self.fydowords[lowerword])
		self.fydowords[lowerword].extend(englishwords)
		currenttime = str(datetime.datetime.now()).split(".")[0]
		log = ("{} [{}]\nOld words: {}\nNew words: {}\n".format(currenttime, lowerword, prevalue, self.fydowords[lowerword]))
		with open(self.logfile, "a") as the_file:
			the_file.write(log)
		print(log)
		await self.saveWords(self.fydowords)

	async def saveWords(self, worddict):
		with open(self.filename, "w") as infile:
			json.dump(worddict, infile)
		print("Save Complete")

	async def loadWords(self):
		with open(self.filename) as outfile:
			x = json.load(outfile)
		print("Load Complete")
		print(x)
		return x

	async def loop(self, array, index=0, lastresults=[], results=[]):
		if index < len(array):
			async for x in arange(array[index]):
				if (index == x == 0):
					results = []
				lastresults.append(x)
				await self.loop(array, index+1, lastresults, results)
				lastresults.pop()
			if (index == 0):
				return list(results)
		else:
			results.append(list(lastresults))

	async def actuallyTranslate(self, words, indexes, translated, fydocombo):
		messages = []
		if len(fydocombo) == 0:
			return messages
		translatedindexes = await self.loop(fydocombo)
		for x in range(len(translatedindexes)):
			c = 0
			translatedindex = translatedindexes[x]
			sentence = []
			for y in range(len(words)):
				if y in indexes:
					normalword = translated[c][translatedindex[c]]
					c+=1
				else:
					normalword = words[y]
				sentence.append(normalword)
			messages.append(" ".join(sentence))
		return messages

	async def translate(self, message):
		words = re.split("[^a-zA-Z]", message)
		indexes = [x for x in range(len(words)) if words[x].lower() in self.fydowords]
		translated = [self.fydowords[words[x].lower()] for x in indexes]
		fydocombo = [len(x) for x in translated]
		return await self.actuallyTranslate(words, indexes, translated, fydocombo)

	async def initialise(self):
		if not self.initialised:
			print("doing init")
			self.initialised = True
			await self.bot.change_presence(activity=discord.Activity(name="Fyd0", type=discord.ActivityType.watching))
			if not (os.path.isfile(self.filename)):
				await self.saveWords(self.fydowords)
			else:
				self.fydowords = await self.loadWords()
			print("ending init")

		async def defaultEmbed(self, icon_url=None, description=None, inline=False, text="Made Possible By Doc And Pleb", name="Fyd0-Speak", title="Fyd0 Translation(s)", color=0xb23aee):
			if icon_url is None:    
				icon_url=self.icon
			if description is None:
				description=self.description
		# Create embeds
			embed = discord.Embed(title=title, description=description, color=color)
			embed.set_author(name=name, icon_url=icon_url)
			embed.set_footer(text=text)
			return embed

		async def embedTranslate(self, translated, msg):
			if (len(translated) > 0 and translated[0] != msg):
				embed = await self.defaultEmbed()
				async for x in arange(len(translated)):
					name = "Translation {}:".format([x+1])
					value = translated[x]
					embed.add_field(name=name, value=value, inline=inline)
			return embed

	#########################
	#		Events			#
	#########################
	async def on_message(self, msg):
		await self.initialise()
		if (msg.author.id in self.translateids and not msg.content.startswith(self.bot.command_prefix(self.bot, "asd")[0])):
			translated = await self.translate(msg.content)
			embed = self.embedTranslate(translated)
			await msg.channel.send(embed=embed)

	#########################
	#	   Commands			#
	#########################
	@commands.command(pass_context=True)
	async def addword(self, ctx, *, msg):
		await self.initialise()
		words = msg.split(" ")
		if len(words) > 0:
			fydoword = words.pop(0)
			await self.addWord(fydoword, words)
			print("Added '{}' as {} to Fyd0's Dictionary".format(fydoword, words))
			
	@commands.command(pass_context=True)
	async def loadwords(self, ctx):
		await self.initialise()
		self.fydowords = await self.loadWords()

	@commands.command(pass_context=True)
	async def savewords(self, ctx):
		await self.initialise()
		await self.saveWords(self.fydowords)

	@commands.command(pass_context=True)
	async def outwords(self, ctx):
		print(json.dumps(self.fydowords).replace("],","],\n"))

	@commands.command(pass_context=True, aliases=["trans"])
	async def translateit(self, ctx, msg: int):
		await self.initialise()
		msgID = await ctx.channel.get_message(msg)
		translated = await self.translate(msgID.content)
		embed = await self.embedTranslate(translated, msgID.content)
		if embed is not None:
			await msg.channel.send(embed=embed)

def setup(bot):
	bot.add_cog(FydoTranslate(bot))