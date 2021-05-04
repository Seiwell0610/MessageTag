import discord
from discord.ext import commands
import os
import asyncio
import sqlite3 as sq3
import re

print(f"{os.path.basename(__file__)}")

# データベースに接続
path = "/home/seiwell/DiscordBot/MessageTag/all_data.db"
connect = sq3.connect(path)
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
    async def add(self, ctx):
        # 正規表現
        regex_discord_message_url = (
            'https://(ptb.|canary.)?discord(app)?.com/channels/'
            '(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})'
        )

        try:
            cursor.execute(f'SELECT * FROM "{ctx.author.id}"').fetchone()
        except sq3.OperationalError:
            cursor.execute(f'CREATE TABLE "{ctx.author.id}"'
                           f'(Tag_name TEXT NOT NULL, Unique_Name TEXT NOT NULL UNIQUE, Message_Link TEXT NOT NULL)')
            connect.commit()

        # 以下、タグ名指定処理
        msg = await ctx.send("登録したいタグ名を入力してください。")

        def check(m):
            return m.content and m.author == ctx.author

        try:
            check_tag_name = await self.bot.wait_for("message", timeout=30, check=check)

        except asyncio.TimeoutError:
            return await ctx.send("タイムアウトしました。")

        else:
            if check_tag_name is not None:
                tag_name = check_tag_name.content
                await check_tag_name.delete()

        # 以下、タイトル指定処理
        await msg.edit(content="タグ名の指定が完了しました。\n続いて、タイトルを入力してください。")

        try:
            check_unique_name = await self.bot.wait_for("message", timeout=30, check=check)

        except asyncio.TimeoutError:
            return await ctx.send("タイムアウトしました。")

        else:
            if check_unique_name is not None:
                unique_name = check_unique_name.content
                if cursor.execute(f'SELECT * FROM "{ctx.author.id}" WHERE Unique_Name = ?', (unique_name,)).fetchone() is not None:
                    return await ctx.send(f"{ctx.author.mention}-> タイトルが重複しているため保存できません。")
                await check_unique_name.delete()

        # 以下、データ指定処理
        await msg.edit(connect="タイトルの指定が完了しました。\n最後に、タグ付けを行いたいメッセージリンクを入力してください。")

        try:
            check_value_name = await self.bot.wait_for("message", timeout=30, check=check)

        except asyncio.TimeoutError:
            return await ctx.send("タイムアウトしました。")

        else:
            if check_value_name is not None:
                value = check_value_name.content
                if re.fullmatch(regex_discord_message_url, value) is None:
                    return await ctx.send(f"{ctx.author.mention}-> メッセージリンクを指定してください。")
                await msg.delete()
                await check_value_name.delete()

            cursor.execute(f'INSERT INTO "{ctx.author.id}" VALUES (?, ?, ?)', (tag_name, unique_name, value))
            connect.commit()
            return await ctx.send(f"{ctx.author.mention}-> 該当のデータを追加しました。")


    @commands.command()
    async def remove(self, ctx):
        try:
            cursor.execute(f'SELECT * FROM "{ctx.author.id}"').fetchone()
        except sq3.OperationalError:
            cursor.execute(f'CREATE TABLE "{ctx.author.id}"'
                           f'(Tag_name TEXT NOT NULL, Unique_Name TEXT NOT NULL UNIQUE, Message_Link TEXT NOT NULL)')
            connect.commit()

        msg = await ctx.send("削除したいデータに関連付けされているタグ名を指定してください。")
        data = cursor.execute(f'SELECT DISTINCT Tag_name From "{ctx.author.id}"').fetchall()
        embed = discord.Embed(title="タグ一覧", description="・{0}".format("\n・".join([row[0] for row in data])),
                              color=discord.Color.purple())
        msg_em_1 = await ctx.send(embed=embed)

        def check(m):
            return m.content and m.author == ctx.author

        try:
            check_tag_name = await self.bot.wait_for("message", timeout=30, check=check)

        except asyncio.TimeoutError:
            return await ctx.send("タイムアウトしました。")

        else:
            if check_tag_name is not None:
                tag_name = check_tag_name.content
                data = cursor.execute(f'SELECT * FROM "{ctx.author.id}" WHERE tag_name=?', (tag_name,)).fetchall()

                # 該当のタグが付いているデータがない場合
                if data is None:
                    return await ctx.send(f"{ctx.author.mention}-> 該当のタグの付いているデータはありませんでした。")

                await check_tag_name.delete()
                await msg_em_1.delete()

        await msg.edit(content="タグ名の指定が完了しました。\n削除したいタイトルを指定してください。")

        # あった場合
        embed = discord.Embed(title=f"**{tag_name}**の付いているタグを{len(data)}件見つかりました。", color=discord.Color.green())
        for row in data:
            embed.add_field(name=f"{row[1]}", value=f"[{row[2][:35]}...]({row[2]})", inline=False)
        msg_em_2 = await ctx.send(embed=embed)

        try:
            check_title_name = await self.bot.wait_for("message", timeout=30, check=check)

        except asyncio.TimeoutError:
            return await ctx.send("タイムアウトしました。")

        else:
            if check_title_name is not None:
                unique_name = check_title_name.content
                await check_title_name.delete()
                await msg_em_2.delete()
                await msg.delete()
                cursor.execute(f'DELETE FROM "{ctx.author.id}" WHERE Tag_Name = ? and Unique_Name = ?',
                               (tag_name, unique_name))
                connect.commit()
                return await ctx.send(f"{ctx.author.mention}-> 該当のデータを削除しました。")

    @commands.command()
    async def mytag(self, ctx):
        data = cursor.execute(f'SELECT DISTINCT Tag_name From "{ctx.author.id}"').fetchall()
        embed = discord.Embed(title="タグ一覧", description="・{0}".format("\n・".join([row[0] for row in data])), color=discord.Color.purple())
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
