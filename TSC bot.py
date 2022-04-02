import discord
from discord.ext import commands,tasks
from discord.commands import Option
import pymongo
import asyncio
import random
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!",intents = intents,status=discord.Status.dnd,activity=discord.Activity(name='Maintenance',type=discord.ActivityType.watching))

x = pymongo.MongoClient("DATABASE STRING")
LB = x.Leaderboard
lb_users = LB.User
lb_teams = LB.Team
team = x.Team
Users = team.Users
uT = x.Users
Team = uT.Team
questions = x.Questions
que = questions.Questions


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
    if Aetasc >= Azurec: team = 'Azure'
    if Azurec >= Vexusc: team = 'Vexus'
    if Vexusc >= Exosc: team = 'Exos'
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

@bot.slash_command( guild_ids = [877460893439512627])
async def ping(ctx):
    """ping pong"""
    await ctx.respond(f"pong: {bot.latency}")

@bot.slash_command( guild_ids = [877460893439512627])
async def leaderboard(ctx,type:Option(str,"Type of leaderboard",required=True,choices=["Player","Team"])):
    """The current leaderboard"""
    await ctx.defer()
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
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title='Leaderboard for Teams',color=0xee9ad9)
        team = lb_teams.find()
        team = team.sort('points',-1)
        for info in team:
            embed.add_field(name=info.get('team'),value=f"{info.get('points')} points!",inline=False)
        await ctx.respond(embed=embed)

@bot.slash_command(guild_ids = [877460893439512627])
@commands.has_permissions(administrator=True)
async def reset(ctx,type:Option(str,"Which type to reset",required=True,choices=["Player","Team"])):
    """Reset the entirety of the leaderboard || NOT SPECIFIC PLAYERS"""
    await ctx.defer()
    if type == 'Player':
        u = Users.find()
        try:
            for users in u:
                Users.delete_one({"user":users.get('user')})
            await ctx.respond("Successfully deleting.")
        except Exception as e:
            await ctx.respond(f'Error: {e}')
    else:
        team_info = lb_teams.find()
        try:
            for info in team_info:
                lb_teams.update_one({'team':info.get('team')},{"$set":{"points":0}})
            await ctx.respond("Successfully deleted.")
        except Exception as e:
            await ctx.respond(f'Error: {e}')

@reset.error
async def reset_error(ctx,error):
    if isinstance(error,commands.MissingPermissions):
        await ctx.respond("Invalid Permissions")
    else:
        ctx.respond(error)

@bot.slash_command(guild_ids = [877460893439512627])
@commands.has_permissions(administrator=True)
async def playerreset(ctx,user:discord.User):
    """Specific player points reset"""
    await ctx.defer()
    try:
        Users.delete_one({'user':user.id})
        await ctx.respond("Successfully deleted.")
    except Exception as e:
        await ctx.respond(f"Error: {e}")

@playerreset.error
async def playerreset_error(ctx,error):
    if isinstance(error,commands.MissingPermissions):
        await ctx.respond("Invalid Permissions")
    else:
        ctx.respond(error)



question_info = {}
@tasks.loop(minutes=5)
async def question_sender():
    global question_info
    await bot.wait_until_ready()
    amount = que.find_one({'question':"STARLORD"})
    amount = amount.get('amount')
    question_num = random.randint(1,amount)
    #channel =  bot.get_channel(955453693866696734)
    channel = bot.get_channel(926681570973196388)
    _question_info = que.find_one({'custom_id':question_num})
    question = _question_info.get("question")
    answer = _question_info.get("answer").lower()
    embed = discord.Embed(color=0xee9ad9)
    embed.add_field(name="TSC-Chat Game", value=question)
    embed.set_author(name="The Study Corner", icon_url=bot.user.avatar.url)
    embed.set_footer(text=f'category: {_question_info.get("category")} || questionID: {_question_info.get("custom_id")} ')
    send = await channel.send(embed=embed)
    question_info = {'answer':answer,'embed':send}
    await asyncio.sleep(1800)
    if question_info != None:
        await channel.send('No one got the answer. Too bad :/')
        question_info = None
    else:
        pass




@bot.event
async def on_message(message):
    global question_info
    if message.content and message.channel.id == 926681570973196388:
        #channel = bot.get_channel(955453693866696734)
        channel = bot.get_channel(926681570973196388)
        message.content = message.content.lower()
        if message.content == question_info.get('answer'):
            question_info = {}
            team = await give_points(message,message.author.id)
            await channel.send(f"{message.author.mention} got the answer. 5 points for team {team}")



question_sender.start()
bot.run("BOT TOKEN")
