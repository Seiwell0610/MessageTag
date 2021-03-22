import discord
from discord.ext import commands
import os

print(f"{os.path.basename(__file__)}")


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="ヘルプ", color=discord.Color.blue())

        embed.add_field(name="#tag <タグ名>", value="該当のタグが付いているデータを表示します。", inline=False)
        embed.add_field(name="#add <タグ名> <タイトル> <メッセージリンク>", value="データを追加します。", inline=False)
        embed.add_field(name="#remove <タグ名> <タイトル>", value="データを削除します。", inline=False)
        embed.add_field(name="#ac", value="ユーザーのデータベースを作成します。", inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
