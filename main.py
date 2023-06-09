import discord
import json
from discord.ext import commands

DB_PATH = "./database.json"
CONFIG_PATH = "./config.json"

# load config from json file
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# load json database to read and write
with open(DB_PATH, "r") as f:
    database = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = False

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), description='pnj', intents=intents)

@bot.event
async def on_ready():
    if config["env"] == "prod":
        await bot.change_presence(status=discord.Status.invisible)

#================================

# add project to database
async def create_project(channel, name, ctx):
    if database.get(channel) is not None:
         await ctx.send("ERREUR : Une suite de quêtes existe déjà sur ce channel !")
         return
    database[channel] = {"name": name, "active": "", "tasks": []}
    save_database()
    await ctx.send("La suite de quêtes [" + name + "] a été créé !")

# delete project from database
async def delete_project(channel, ctx):
    if database.get(channel) is None:
         await ctx.send("ERREUR : Pas de suite de quêtes sur ce channel !")
         return
    database[channel].pop()
    save_database()
    await ctx.send("La suite de quêtes a été supprimé !")

# see project tasks
async def see_project(channel, ctx):
    if database.get(channel) is None:
         await ctx.send("ERREUR : Pas de suite de quêtes sur ce channel !")
         return

    lines = []
    lines.append("======= " + database[channel]["name"] + " =======")
    if database[channel]["tasks"] == []:
        lines.append("Aucune quête en cours...")
        message = '\n'.join(lines)
        await ctx.send(message)
        return
    for index, task in enumerate(database[channel]["tasks"]):
        # get channel used by context
        channel = ctx.channel

        lines.append("[" + str(index + 1) + "] " + task["description"] + " - " + task["responsible"] + " - " + task["status"])
    message = '\n'.join(lines)
    await ctx.send(message)

#================================

# create task
def create_task(channel, task, creator):
    database[channel]["tasks"].append({"description": task, "status": "NEW", "responsible": creator})
    save_database()

# remove task
def delete_task(channel, task_number):
    task = database[channel]["tasks"][int(task) - 1]
    database[channel]["tasks"].remove(task)
    save_database()

# assign responsable to task
def assign_responsible(channel, task, responsible, ctx):
    # get member name from mention
    if responsible[0] == "<":
        responsible = ctx.guild.get_member(int(responsible[2:-1])).name

    database[channel]["tasks"][int(task) - 1]["responsible"] = responsible
    save_database()

# finish task
def finish_task(channel, task):
    database[channel]["tasks"][int(task) - 1]["status"] = "DONE"
    save_database()

# cancel task
def cancel_task(channel, task):
    database[channel]["tasks"][int(task) - 1]["status"] = "CANCELLED"
    save_database()

#================================

# save database to json file
def save_database():
    with open(DB_PATH, "w") as f:
        json.dump(database, f)

@bot.command()
async def hello(ctx):
    await ctx.send("Grunt Grunt !")

# ========== project commands ==========
# help command
@bot.command()
async def phelp(ctx):
    await ctx.send("Liste des commandes : \n!cp <nom> : créer une suite de quêtes \n!dp : supprimer la suite de quêtes \n!sp : voir les quêtes en cours \n!ct <quête> : créer une quête \n!dt <numéro> : supprimer une quête \n!rt <numéro> <responsable> : Donner la quête à un joueur\n!ft <numéro> : rendre une quête \n!cat <numéro> : annuler une quête")

# create new project
@bot.command()
async def cp(ctx, name):
    await ctx.send("Création de la suite de quêtes " + name + "...")
    channel = ctx.channel.name
    await create_project(channel, name, ctx)

# delete project
@bot.command()
async def dp(ctx, task):
    channel = ctx.channel.name
    await delete_project(channel, task)

# see project
@bot.command()
async def sp(ctx):
    channel = ctx.channel.name
    await see_project(channel, ctx)

# ========== tasks commands ==========
# create task and store user data to mention him
@bot.command()
async def ct(ctx, *args):
    channel = ctx.channel.name
    creator = ctx.author.name
    description = ' '.join(args)
    create_task(channel, description, creator)

# delete task
@bot.command()
async def dt(ctx, task_number):
    channel = ctx.channel.name
    delete_task(channel, task_number)

# assign responsible to task
@bot.command()
async def rt(ctx, task_number, responsible):
    channel = ctx.channel.name
    assign_responsible(channel, task_number, responsible, ctx)

# finish task
@bot.command()
async def ft(ctx, task_number):
    channel = ctx.channel.name
    finish_task(channel, task_number)

# cancel task
@bot.command()
async def cat(ctx, task_number):
    channel = ctx.channel.name
    cancel_task(channel, task_number)

# ========== END ==========

# run bot using token on config.json
bot.run(config["token"])
