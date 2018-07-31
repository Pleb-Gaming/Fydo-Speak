from discord.ext import commands
from discord.ext.commands import bot
from discord import *
from os import getcwd
import asyncio
import datetime
import discord
import io
import json
import os.path
import re

class FydoTranslate:
    #########################
    #  Default Values Here  #
    #########################
    def __init__(self, bot):
        self.bot = bot
        self.initialised = False
        self.configname = "cogs/fydo/config.json"

    #########################
    #    Actual Functions   #
    #########################
    async def saveFile(self, data, filename, flag='w'):
        with open(filename, flag) as file:
            if type(data) is list:
                for x in data:
                    file.write(x)
            else:
                file.write(data)
    async def createFile(self, filename, data=""):
        if not os.path.isfile(filename):
            await self.saveFile(data, filename, flag='w+')
    async def loadFile(self, filename):
        await self.createFile(filename)
        with open(filename, "r+") as file:
            return file.readlines()

    async def saveJSON(self, data, filename):
        await self.createFile(filename, data)
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    async def loadJSON(self, filename, data="{}"):
        await self.createFile(filename, data)
        with open(filename) as file:
            return json.load(file)

    async def loadConfigDefaults(self):
        self.config = await self.loadJSON(self.configname)
        self.config.setdefault("description",       "Translation for whatever the hell Fyd0 just said")
        self.config.setdefault("icon",              "https://cdn.discordapp.com/avatars/456691275178049558/a9b4641d2469f9cb6da79846c8c9d503.png?size=256")
        self.config.setdefault("filename",          "cogs\\fydo\\FydoDictionary.txt")
        self.config.setdefault("logfile",           "cogs\\fydo\\FydoLog.txt")
        self.config.setdefault("translateids",      [162718727622623232])
        self.config.setdefault("defaultfydowords",  {})
        self.config.setdefault("debug",             False)
        self.config.setdefault("color",             0xb23eae)
        self.config.setdefault("version",           "98")
        self.config.setdefault("versiontitle",      "Electric Boogaloo")
        print(self.config)
    async def saveConfigDefaults(self):
        # Pop fydowords, save config, push fydowords
        fydowordstr = json.dumps(self.config.setdefault("fydowords", {}))
        del self.config['fydowords']
        await self.saveJSON(self.config, self.configname)
        self.config['fydowords'] = json.loads(fydowordstr)
    async def addWord(self, fydoword, englishwords):
        lowerword = fydoword.lower()
        fydowords = self.config['fydowords']
        prevalue = list(fydowords.setdefault(lowerword, set()))
        fydowords[lowerword] = list(fydowords[lowerword].union(englishwords))
        currenttime = str(datetime.datetime.now()).split(".")[0]
        log = (f"{currenttime} [{lowerword}]\nOld words: {prevalue}\nNew words: {self.config['fydowords'][lowerword]}\n")
        print(log)
        await self.saveFile(log, self.config['logfile'], "a")
        await self.saveWords(self.config['fydowords'])
    async def saveWords(self, worddict):
        await self.saveJSON(worddict, self.config['filename'])
        print("Save Complete")
    async def loadWords(self):
        x = await self.loadJSON(self.config['filename'])
        return x

    async def starts_with_prefix(self, message):
        prefixes = await self.bot.get_prefix(message)
        print(prefixes)
        for x in prefixes:
            if message.startswith(x):
                return True
        return False

    async def loop(self, array, index=0, lastresults=[], results=[]):
        if index < len(array):
            # arange waz here
            # async for x in range(array[index]):
            for x in range(array[index]):
                if (index == x == 0):
                    results = []
                lastresults.append(x)
                await self.loop(array, index+1, lastresults, results)
                lastresults.pop()
            if (index == 0):
                return list(results)
        else:
            results.append(list(lastresults))

    # Translation Block
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
        words = re.split("[^a-zA-Z0-9]", message)
        indexes = [x for x in range(len(words)) if words[x].lower() in self.config['fydowords']]
        translated = [self.config['fydowords'][words[x].lower()] for x in indexes]
        fydocombo = [len(x) for x in translated]
        return await self.actuallyTranslate(words, indexes, translated, fydocombo)

    # Embed Block
    async def defaultEmbed(self, icon_url=None, description=None, text="Made Possible By Doc And Pleb", name="Fyd0-Speak", title="Fyd0 Translation(s)", color=None):
        #Set defaults
        icon_url=self.config.setdefault('icon', "https://cdn.discordapp.com/avatars/456691275178049558/a9b4641d2469f9cb6da79846c8c9d503.png?size=256")
        description=self.config.setdefault('description', "Translation for whatever the hell Fyd0 just said")
        color=self.config.setdefault('color', 0xb23eae)
        # Create embeds
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_author(name=name, icon_url=icon_url)
        embed.set_footer(text=text)
        return embed
    async def versionEmbed(self, msg, inline=True):
        embed = await self.defaultEmbed()
        embed.add_field(name=name, value=value, inline=inline)
        embed.add_field(name=name, value=value, inline=inline)
        return embed    
    async def embedTranslate(self, translated, msg, inline=False):
        if not (len(translated) > 0 and translated[0] != msg):
            return None
        embed = await self.defaultEmbed()
        # arange waz here
        # async for x in range(len(translated)):
        for x in range(len(translated)):
            name = "Translation {}:".format([x+1])
            value = translated[x]
            embed.add_field(name=name, value=value, inline=inline)
        return embed
    async def translateDebugPrint(self, ctx, msg):
        translated = await self.translate(msg)
        embed = await self.embedTranslate(translated, msg)
        if embed is not None:
            await ctx.channel.send(embed=embed)
    async def translatePrint(self, ctx, msg):
        translated = await self.translate(msg)
        embed = await self.embedTranslate(translated, msg)
        if embed is not None:
            await ctx.channel.send(embed=embed)
    async def debugPrint(self, msg):
        if self.config['debug']:
            print(msg)
    
    async def updateCtx(self, ctx, kwargs):
        for key, value in kwargs.iteritems():
            ctx.__dict__[key] = value
    async def initialise(self):
        # Code folding aylmao
        if not self.initialised:
            print("doing init")
            await self.loadConfigDefaults()
            await self.saveConfigDefaults()
            temp = await self.loadWords()
            self.config['fydowords'] = (temp if len(temp) > 0 else self.config['defaultfydowords'])
            print(len(temp))
            print(len(self.config['fydowords']))
            self.initialised = True
    async def commandStart(self, ctx, kwargs):
        await self.initialise()
        await self.updateCtx(ctx, kwargs)
    #########################
    #        Events         #
    #########################
    async def on_message(self, ctx):
        await self.initialise()
        if (ctx.author.id in self.config['translateids'] and not await self.starts_with_prefix(ctx.content)):
            await self.translatePrint(ctx, ctx.content)
        # await self.bot.process_commands(msg)

    #########################
    #       Commands        #
    #########################

    @commands.command(pass_context=True)
    async def addword(self, ctx, *, msg):
        await self.initialise()
        words = msg.split(" ")
        if len(words) > 0:
            fydoword = words.pop(0)
            await self.addWord(fydoword, words)
            print("Added '{}' as {} to Fyd0's Dictionary".format(fydoword, words))
        await ctx.message.delete()
            
    @commands.command(pass_context=True)
    async def loadwords(self, ctx):
        await self.initialise()
        self.config['fydowords'] = await self.loadWords()
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def savewords(self, ctx):
        await self.initialise()
        await self.saveWords(self.config['fydowords'])
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def outwords(self, ctx):
        await self.initialise()
        print(json.dumps(self.config['fydowords']).replace("],","],\n"))
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def download(self, ctx, filename):
        await self.initialise()
        await ctx.channel.send(file=discord.File("{}/cogs/fydo/{}".format(getcwd(), filename)))
        await ctx.message.delete()

    @commands.command(pass_context=True, aliases=["trans"])
    async def translateit(self, ctx, *, msg):
        await self.initialise()
        if self.config['debug']:
            await self.translatePrint(ctx, msg)
        else:
            await self.translateDebugPrint(ctx, msg)
        await ctx.message.delete()

    @commands.command(pass_context=True, aliases=["transid"])
    async def translateid(self, ctx, msg: int):
        await self.initialise()
        try:
            target = await ctx.channel.get_message(msg)
            (await self.translateDebugPrint(ctx, target.content) if self.config['debug'] else await self.translatePrint(ctx, target.content))
        except NotFound:
            print(f"Error: Message with id {msg} not found")
        await ctx.message.delete()

    @commands.command(pass_context=True, aliases=["fd"])
    async def fydodebug(self, ctx):
        await self.initialise()
        print(str(ctx.__dict__).replace(",", ",\n"))
        self.config['debug'] = not self.config['debug']
        await ctx.channel.send(f"Debug mode: {self.config['debug']}")
        await ctx.message.delete()
        
    @commands.command(pass_context=True, aliases=["c"])
    async def changelog(self, ctx):
        await self.initialise()
        await ctx.channel.send(f"```fix\nVersion: {self.config['version']}\nVersion Title: {self.config['versiontitle']}```")
        await ctx.message.delete()

    @commands.command(pass_context=True)
    async def test(self, ctx):
        commands = {
            "0": {"command": self.outwords, "message": ctx.channel.send("?outwords"), "enabled": True, "startmsg": "Start outwords"},
            "1": {"command": self.loadwords, "message": ctx.channel.send("?loadwords"), "enabled": True, "startmsg": "Start loadwords"},
            "2": {"command": self.savewords, "message": ctx.channel.send("?savewords"), "enabled": True, "startmsg": "Start savewords"},
            "3": {"command": self.addword, "message": ctx.channel.send("?addword jonk God"), "enabled": True, "startmsg": "Start addword"},
            #"4": {"command": self.removeword, "message": ctx.channel.send("?removeword jonk God"), "enabled": True, "startmsg": "Start removeword"},
            "5": {"command": self.download, "message": ctx.channel.send("?download FydoDictionary.txt"), "enabled": True, "startmsg": "Start download"},
            "6": {"command": self.translateit, "message": ctx.channel.send("?translateit"), "enabled": True, "startmsg": "Start translateit"},
            "7": {"command": self.translateid, "message": ctx.channel.send("?translateid"), "enabled": True, "startmsg": "Start translateid"},
            "8": {"command": self.fydodebug, "message": ctx.channel.send("?fydodebug"), "enabled": True, "startmsg": "Start fydodebug"}
        }

        for command in commands.values():
            print(command['startmsg'])
            print(command['command'])
            print(await command['message'])
            #await ctx.invoke()

        #for command in commands:
        #    await ctx.invoke(command['command'])
        #message = (await ctx.channel.send("Starting Test"))
        #print(messageID)
        #await ctx.invoke(self.outwords)
        #await ctx.invoke(self.loadwords)
        #await ctx.invoke(self.savewords)
        #await ctx.invoke(self.addword, ["jonk God"])
        #await ctx.invoke(self.removeword, ["jonk God"])
        #await ctx.invoke(self.download, [self.config['filename']])
        #await ctx.invoke(self.translateit, ["vundafa, feel gud mang"])
        #await ctx.invoke(self.translateid, [messageID.id])
        #await ctx.invoke(self.fydodebug)
        #await ctx.invoke(self.test)
def setup(bot):
    bot.add_cog(FydoTranslate(bot))
