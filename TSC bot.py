import discord
from discord.ext import commands, tasks
from discord import app_commands
import pymongo
import asyncio
import random
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!",intents = intents,status=discord.Status.dnd,activity=discord.Activity(name='TSC',type=discord.ActivityType.watching))

x = pymongo.MongoClient("connection string")
LB = x.Leaderboard
lb_users = LB.User
lb_teams = LB.Team
team = x.Team
Users = team.Users
uT = x.Users
Team = uT.Team
questions = x.Questions
que = questions.Questions

#Maintenence comannds
@bot.command()
@commands.is_owner()
async def syncguild(ctx):
    await bot.tree.sync(guild=ctx.guild)
    await ctx.send("Successfully Synced")


@bot.command()
@commands.is_owner()
async def syncall(ctx):
    await bot.tree.sync()
    await ctx.send("Successfully Synced to all guilds")

@bot.command()
@commands.is_owner()
async def starteloop(ctx):
    question_sender.start()
    await ctx.send("Successfully Started")


def assign_team(id):
    team = 'Aetas'
    Aetasc = 0
    Azurec = 0
    Vexusc = 0
    Exosc = 0
    Aetas = Users.find({'team':'Aetas'})
    Azure = Users.find({'team': 'Azure'})
    Vexus = Users.find({'team': 'Vexus'})
    Exos = Users.find({'team': 'Exos'})
    for i in Aetas:
        Aetasc = Aetasc + 1
    for i in Azure:
        Azurec = Azurec + 1
    for i in Vexus:
        Vexusc = Vexusc + 1
    for i in Exos:
        Exosc = Exosc + 1
    if Aetasc > Azurec: team = 'Azure'
    if Azurec > Vexusc: team = 'Vexus'
    if Vexusc > Exosc: team = 'Exos'
    Users.insert_one({'user':id,'team':team})
    return team


async def give_points(message,id):
    x = Users.find_one({'user': id})
    if x == None:
        team = assign_team(id)
        await message.channel.send(f"{message.author.mention} you are now on team {team}")
        x = Users.find_one({'user': id})
    else:
        team = x.get('team')
    team_data = lb_teams.find_one({"team":team})
    points = team_data.get('points')
    points = points + 5
    lb_teams.update_one({'team':team},{"$set":{'points':points}})
    point = x.get('points')
    if point == None or point == 0:
        Users.update_one({'user':id},{"$set":{'points':1}})
    else:
        point = point + 1
        Users.update_one({'user': id}, {"$set": {'points': point}})
    return team


@bot.event
async def on_ready():
    print(f'{bot.user} is online.')


@bot.tree.command()
async def ping(ctx):
    """ping pong"""
    await ctx.response.send_message(f"pong: {bot.latency}")

@bot.tree.command()
async def team(ctx:discord.Interaction,user:discord.User = None):
    """See who is on what team."""
    await ctx.response.defer()


@bot.tree.command()
async def repo(ctx:discord.Interaction):
    """The Repository for this bot"""
    await ctx.response.send_message("https://github.com/starlordXD69/TheStudyCornerBot")
types= []
Player = app_commands.Choice(name='Player',value='Player')
team_option = app_commands.Choice(name='Team',value='Team')
types.append(Player)
types.append(team_option)
@bot.tree.command()
@app_commands.choices(type=types)
async def leaderboard(ctx:discord.Interaction,type:str):
    """The current leaderboard"""
    await ctx.response.defer()
    if type == "Player":
        user = Users.find()
        user = user.sort('points', -1)
        embed = discord.Embed(title='The top 5 Users in the Server',color=0xee9ad9)
        count = 0
        for i in user:
            if count == 5:
                break
            user = bot.get_user(i.get('user'))
            embed.add_field(name=user.name,value=f'{i.get("points")} points!',inline=False)
            count = count + 1
        await ctx.followup.send(embed=embed)
    else:
        embed = discord.Embed(title='Leaderboard for Teams',color=0xee9ad9)
        team = lb_teams.find()
        team = team.sort('points',-1)
        for info in team:
            embed.add_field(name=info.get('team'),value=f"{info.get('points')} points!",inline=False)
        await ctx.followup.send(embed=embed)

@bot.tree.command(guild=discord.Object(630014101887778816))
@commands.has_permissions(administrator=True)
@app_commands.choices(type=types)
async def reset(ctx:discord.Interaction,type:str):
    """Reset the entirety of the leaderboard || NOT SPECIFIC PLAYERS"""
    await ctx.response.defer()
    if type == 'Player':
        u = Users.find()
        try:
            for users in u:
                Users.delete_one({"user":users.get('user')})
            await ctx.followup.send("Successfully deleting.")
        except Exception as e:
            await ctx.followup.send(f'Error: {e}')
    else:
        team_info = lb_teams.find()
        try:
            for info in team_info:
                lb_teams.update_one({'team':info.get('team')},{"$set":{"points":0}})
            await ctx.followup.send("Successfully deleted.")
        except Exception as e:
            await ctx.followup.send(f'Error: {e}')


@bot.tree.command(guild=discord.Object(630014101887778816))
@commands.has_permissions(administrator=True)
async def playerreset(ctx:discord.Interaction,user:discord.User):
    """Specific player points reset"""
    await ctx.response.defer()
    try:
        Users.delete_one({'user':user.id})
        await ctx.followup.send("Successfully deleted.")
    except Exception as e:
        await ctx.followup.send(f"Error: {e}")
question_info = {}
@tasks.loop(hours=1)
async def question_sender():
    global question_info
    await bot.wait_until_ready()
    amount = que.find_one({'question':"STARLORD"})
    amount = amount.get('amount')
    question_num = random.randint(1,amount)
    channel = bot.get_channel(931869372425830410)
    _question_info = que.find_one({'custom_id':question_num})
    question = _question_info.get("question")
    answer = _question_info.get("answer").lower()
    embed = discord.Embed(color=0xee9ad9)
    embed.add_field(name="TSC-Chat Game", value=question)
    embed.set_author(name="The Study Corner", icon_url=bot.user.avatar.url)
    embed.set_footer(text=f'category: {_question_info.get("category")} || questionID: {_question_info.get("custom_id")} ')
    send = await channel.send(embed=embed)
    try:
        await send.pin()
        await channel.purge(limit=1,reason="Deleting pin message")
    except:
        pass
    question_info = {'answer':answer,'embed':send,'channel':channel.id}
    question_checker.start()
@tasks.loop(minutes=31)
async def question_checker():
    global question_info
    await asyncio.sleep(1800)
    if question_info != None:
        channel = bot.get_channel(question_info.get('channel'))
        sendt = question_info.get('embed')
        await channel.send('No one got the answer. Too bad :/')
        try:
            await sendt.unpin()
            await sendt.delete()
        except:
            pass
        question_info = None
        question_checker.stop()

@bot.event
async def on_message(message):
    global question_info
    await bot.process_commands(message)
    if message.content and message.channel.id == 931869372425830410:
        if message.author.id == bot.user.id:
            return
        else:
            channel = bot.get_channel(931869372425830410)
            message.content = message.content.lower()
            if message.content == question_info.get('answer'):
                embed = question_info.get("embed")
                try:
                    await embed.unpin()
                    await embed.delete()
                    await message.delete()
                except:
                    pass
                question_info = {}
                team = await give_points(message,message.author.id)
                await channel.send(f"<@{message.author.id}> got the answer. 5 points for team {team}")




bot.run("TOKEN")
