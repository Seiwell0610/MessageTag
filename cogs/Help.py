import discord
from discord.ext import commands
import os

print(os.path.basename(__file__))


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="ヘルプ", color=discord.Color.blue())

        embed.add_field(name="#tag", value="該当のタグが付いているデータを表示します。", inline=False)
        embed.add_field(name="#add", value="データを追加します。", inline=False)
        embed.add_field(name="#remove", value="データを削除します。", inline=False)
        embed.add_field(name="#mytag", value="登録されているタグの一覧を表示", inline=False)
        embed.add_field(name="#ac", value="ユーザーのデータベースを作成します。", inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
