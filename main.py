from ast import Await
from atexit import register
from http import client
from lib2to3.pgen2 import token
import discord
from discord.ext import commands
import mysql.connector
from mysql.connector import errorcode
from discord.utils import get

token = '' #your token here

db_manager = "DB" #this role controls who can see the database data 
db_host =  "localhost"
db_user = "root"        #These Varaibles control DB connectivity and queries
db_password = "root"
db_name = "test"

welcome_message_channel = "general" #this sets to which channel the welcome message to be send
reaction_notification_channel = 'bot' #this sets to which channel the notification to be send
reaction_notification_channel = 'bot' #to specify the channel to give notification about the reactions added

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = '!', intents=intents)  #bot prefix is "!"

@bot.command(pass_context=True)
async def register(ctx,username):
    try :
        db = mysql.connector.connect(
            host = db_host,
            user = db_user,
            password = db_password,
            database = db_name
        )
        mycursor = db.cursor()
        discord_id = str(ctx.author)
        discord_username = str(username)
        print(discord_username)
        print(discord_id)
        sql = "INSERT INTO discord_userdata VALUES(%s,%s)"
        print(sql)
        val = (discord_username,discord_id)
        mycursor.execute(sql,val)
        db.commit()
        emoji = '\N{THUMBS UP SIGN}'
        message = await ctx.fetch_message(ctx.message.id) #this returns the details about the message send using the CTX
        await message.add_reaction(emoji) 
    except mysql.connector.Error as error :
        print("Error : {}".format(error))
        if error.errno == errorcode.ER_DUP_ENTRY :
            await ctx.send("Duplicate Entry!!")
    finally :
        if db.is_connected():
            db.close()   

@bot.command(pass_context=True)
@commands.has_role(db_manager)
async def names(ctx):
    db = mysql.connector.connect(
        host = db_host,
        user = db_user,
        password = db_password,
        database = db_name
    )
    mycursor = db.cursor()
    mycursor.execute("SELECT username FROM discord_userdata")
    result = mycursor.fetchall()
    count = mycursor.rowcount
    db.close()
    names = ""
    for x in result:
        print(x[0])
        names = names + "\n" + x[0]
    names = names + "\n----------------------------\nTotal Count : " + str(count)
    user = await bot.fetch_user(ctx.author.id)
    await ctx.send(names)

@bot.event
async def on_message(message):
    if message.author == bot.user :
        return
    await bot.process_commands(message) 

@bot.command(pass_context=True)
async def role(ctx,role):
    author = ctx.message.author 
    print(role)
    guild = ctx.guild
    if get(guild.roles, name=role):
        await ctx.send(f"Hi {author.mention},Role already exists")
    else:      
        role_obj = await guild.create_role(name=role)
        await author.add_roles(role_obj)
        await ctx.send(f"hey {author.mention} has assigned a role called: {role}")

@bot.event
async def on_raw_reaction_add(payload):
    message_author = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id) # returns the details about the message in which the reaction is added
    if payload.member == bot.user :
        return
    channel = discord.utils.get(bot.get_all_channels(), name=reaction_notification_channel) 
    await channel.send("{} reacted to {}".format(payload.member,message_author.author))   # "payload.member" returns the id of user who added the reaction

@bot.event
async def on_member_join(member):
     for channel in bot.get_all_channels():
        if channel.name == 'bot':
            await channel.send(f'Hi {member.mention}, Welcome to {member.guild.name}')

@bot.event
async def on_ready():
    print('we have logged in as {0.user}'.format(bot))


bot.run(token)