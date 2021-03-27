import discord
from discord.ext import commands
import os
import sqlite3 as sq3
import re

print(f"{os.path.basename(__file__)}")

# データベースに接続
connect = sq3.connect("all_data.db")
cursor = connect.cursor()


class SetTags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tag(self, ctx, tag_name: str = None):
        try:
            # タグを指定していない場合
            if tag_name is None:
                return await ctx.send(f"{ctx.author.mention}-> タグを指定してください。")

            # 該当のタグが付いているデータを取得
            data = cursor.execute(f'SELECT * FROM "{ctx.author.id}" WHERE tag_name=?', (tag_name, )).fetchall()

            # 該当のタグが付いているデータがない場合
            if data is None:
                return await ctx.send(f"{ctx.author.mention}-> 該当のタグの付いているデータはありませんでした。")

            # あった場合
            embed = discord.Embed(title=f"**{tag_name}**の付いているタグを{len(data)}件見つかりました。", color=discord.Color.green())
            for row in data:
                embed.add_field(name=f"{row[1]}", value=f"[{row[2][:35]}...]({row[2]})", inline=False)
            await ctx.send(embed=embed)

        except sq3.OperationalError:
            cursor.execute(f'CREATE TABLE "{ctx.author.id}"'
                           f'(Tag_name TEXT NOT NULL, Unique_Name TEXT NOT NULL UNIQUE, Message_Link TEXT NOT NULL)')
            connect.commit()
            await ctx.send(f"{ctx.author.mention}-> DBを作成しました。再度コマンドを実行してみて下さい。")

    @commands.command()
    async def add(self, ctx, tag_name: str = None, unique_name: str = None, value: str = None):
        # 正規表現
        regex_discord_message_url = (
            'https://(ptb.|canary.)?discord(app)?.com/channels/'
            '(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})'
        )

        try:
            if tag_name is None:
                return await ctx.send(f"{ctx.author.mention}-> タグを指定してください。")

            if unique_name is None:
                return await ctx.send(f"{ctx.author.mention}-> タイトルを指定してください。")

            if value is None:
                return await ctx.send(f"{ctx.author.mention}-> データを指定してください。")

            if re.fullmatch(regex_discord_message_url, value) is None:
                return await ctx.send(f"{ctx.author.mention}-> メッセージリンクを指定してください。")

            if cursor.execute(f'SELECT * FROM "{ctx.author.id}" WHERE Unique_Name = ?', (unique_name, )).fetchone() is not None:
                return await ctx.send(f"{ctx.author.mention}-> タイトルが重複しているため保存できません。")

            cursor.execute(f'INSERT INTO "{ctx.author.id}" VALUES (?, ?, ?)', (tag_name, unique_name, value))
            connect.commit()
            return await ctx.send(f"{ctx.author.mention}-> 該当のデータを追加しました。")

        except sq3.OperationalError:  # ユーザーのテーブルが存在しない場合、自動的に作成
            cursor.execute(f'CREATE TABLE "{ctx.author.id}"'
                           f'(Tag_name TEXT NOT NULL, Unique_Name TEXT NOT NULL UNIQUE, Message_Link TEXT NOT NULL)')
            connect.commit()
            await ctx.send(f"{ctx.author.mention}-> DBを作成しました。再度コマンドを実行してみて下さい。")


    @commands.command()
    async def remove(self, ctx, tag_name: str = None, unique_name: str = None):
        try:
            if tag_name is None:
                return await ctx.send(f"{ctx.author.mention}-> タグを指定してください。")

            if unique_name is None:
                return await ctx.send(f"{ctx.author.mention}-> タイトルを指定してください。")

            data = cursor.execute(f'SELECT * FROM "{ctx.author.id}" WHERE Tag_Name = ? and Unique_Name = ?', (tag_name, unique_name, )).fetchone()

            if data is None:
                return await ctx.send(f"{ctx.author.mention}-> 該当のデータがありません。")

            cursor.execute(f'DELETE FROM "{ctx.author.id}" WHERE Tag_Name = ? and Unique_Name = ?', (tag_name, unique_name))
            connect.commit()
            return await ctx.send(f"{ctx.author.mention}-> 該当のデータを削除しました。")

        except sq3.OperationalError:
            cursor.execute(f'CREATE TABLE "{ctx.author.id}"'
                           f'(Tag_name TEXT NOT NULL, Unique_Name TEXT NOT NULL UNIQUE, Message_Link TEXT NOT NULL)')
            connect.commit()
            await ctx.send(f"{ctx.author.mention}-> DBを作成しました。再度コマンドを実行してみて下さい。")

    @commands.command()
    async def mytag(self, ctx):
        data = cursor.execute(f'SELECT DISTINCT Tag_name From "{ctx.author.id}"').fetchall()
        description = ''
        for _ in data:
            description += "・" + _[0] + "\n"
        embed = discord.Embed(title="タグ一覧", description=description, color=discord.Color.purple())
        await ctx.send(embed=embed)

    @commands.command()
    async def ac(self, ctx):
        try:
            cursor.execute(f'SELECT * FROM "{ctx.author.id}"')

        except sq3.OperationalError:
            cursor.execute(f'CREATE TABLE "{ctx.author.id}"'
                           f'(Tag_name TEXT NOT NULL, Unique_Name TEXT NOT NULL UNIQUE, Message_Link TEXT NOT NULL)')
            connect.commit()
            await ctx.send(f"{ctx.author.mention}-> DBを作成しました。")


def setup(bot):
    bot.add_cog(SetTags(bot))
