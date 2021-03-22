import discord
import asyncio
from discord.ext import commands
import os
import traceback
from dotenv import load_dotenv

load_dotenv()  # 環境変数を.envから設定

token = os.environ["TOKEN"]
prefix = "#"
loop = asyncio.new_event_loop()


async def run():
    bot = MyBot()
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.logout()


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(prefix), loop=loop, intents=discord.Intents.all())
        self.remove_command('help')

    async def on_ready(self):
        path = "./cogs"
        for cog in os.listdir(path):
            if cog.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{cog[:-3]}")
                except commands.ExtensionAlreadyLoaded:
                    self.reload_extension(f"cogs.{cog[:-3]}")

        await self.change_presence(activity=discord.Game(name=f"{prefix}help"))


if __name__ == '__main__':
    try:
        print(f"Discord.pyのバージョン：{discord.__version__}")
        print("起動完了")

        main_task = loop.create_task(run())
        loop.run_until_complete(main_task)
        loop.close()

    except Exception as error:
        print("エラー情報\n" + traceback.format_exc())
