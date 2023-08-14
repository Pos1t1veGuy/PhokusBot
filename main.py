async def find_channel(id:int):
  try:
    try:
      return await client.fetch_channel(id)
    except:
      return await client.fetch_user(id)
  except:
    pass

async def update_libraries():
  global sublibs
  for lib in sublibs:
    try:
      module = il.import_module(lib)
      il.reload(module)
      print(f"Библиотека {lib} обновлена")
      
      global_vars = globals()
      for var_name in dir(module):
        if not var_name.startswith("__"):
          global_vars[var_name] = getattr(module, var_name)
              
    except ImportError:
      print(f"{Fore.RED}Не удалось импортировать библиотеку {lib}{Fore.RESET}")

async def ginit():
  global white_list, black_list, guilds, author, guilds_cfg

  await update_libraries()
  gs = []

  for g in guilds_cfg:
    kwargs = {key: value for key, value in g.items() if not key in ["id","prefix","name"]}
    gs.append(guild(globals(), g["id"], g["prefix"], g["name"], **kwargs))
  
  guilds = Guilds(gs, white_list, black_list)

async def bot_log(msg:str, guild=None, channel=None, user=None, cmd=None, type='message'):
  global logging, cmdLogger, eventLogger, logmsg, tz

  gn, gi = ( guild.name, guild.id ) if guild else ( None, None )
  cn, ci = ( channel.name, channel.id ) if channel else ( None, None )
  un, ui = ( user.name, user.id ) if user else ( None, None )
  if tz:
    time = str(datetime.now(tz)).split('.')[0]
  else:
    time = str(datetime.now()).split('.')[0]

  sep = 18
  
  gn = ( gn if len(gn) < sep+3 else gn[:sep]+"..." ) if gn else None
  cn = ( cn if len(cn) < sep+3 else cn[:sep]+"..." ) if cn else None
  un = ( un if len(un) < sep+3 else un[:sep]+"..." ) if un else None

  console_info = logmsg.format(time, gn, cn, un, msg)
  file_info = logmsg.format(time, gi, ci, ui, msg)

  types = {
    'message': Fore.RESET,
    'success': Fore.GREEN,
    'warning': Fore.YELLOW,
    'error': Fore.RED,
  }
  color = types[type] if type in types.keys() else Fore.RESET
  file = cmdLogger if cmd else eventLogger
  
  try:
    if logging:
      print(color+console_info+Fore.RESET)
      open(file, 'a').write(f'{file_info}\n')

  except FileNotFoundError:
    print(color+console_info+Fore.RESET)
    open(file, 'w').write(f'{file_info}\n')
    await main_init(None, globals(), [], 0)

import random as r
import importlib as il

from threading import Thread as th
from datetime import datetime

from disnake.ext import tasks
import disnake as discord

from config import *
from server import keep_alive
from setup import Guilds, guild
from commands import *

client = discord.Client(intents=discord.Intents.all())
modules = [m.__name__ for m in sys.modules.values() if m and not '.' in m.__name__ and not '_' in m.__name__]

@client.event
async def on_ready():
  global author, guilds
  await clear_console()

  author = await find_channel(int(author)) if author else None
  await ginit()
  
  for gld in guilds:
    for name, id in gld.channels.items():
      channel = await find_channel(id)
      if id is None:
        await bot_log(f"{name} не найден", type="warning")
      gld.channels[name] = channel

  await bot_log(f"Начинаю работу как {client.user}", type="success")

  change_status.start()
  secloop.start()

@tasks.loop(seconds=1)
async def secloop():
    pass
@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Activity(name=next(status), type=discord.ActivityType.playing))

@client.event
async def on_member_join(member):
  global author
  try:
    if member.guild.id in guilds.ids.keys():
      if guilds[member.guild.id].welcomes and "welcome" in list(guilds[member.guild.id]):
        await guilds[member.guild.id]["welcome"].send(
          r.choice( guilds[member.guild.id].welcomes ).format(str( member.id ))
        )
      if guilds[member.guild.id].welcome_role:
        role = discord.utils.get(member.guild.roles, id=int(guilds[member.guild.id].welcome_role))
        await member.add_roles(role)
    await bot_log(f'joined {member.id}', guild=member.guild, user=member)
    
  except Exception as ex:
      await response(author, f'Неизвестная ошибка бота {ex}')
      lines = ""
      for name, num, line in await rarse_exception(ex):
        lines += f"\n  {name} > {num}: {line}"
        await response(author, f"{name}\n > {num}: {line}")
      await bot_log('on_member_join', guild=member.guild, user=member, type="error")

@client.event
async def on_member_remove(member):  
  try:
    if member.guild.id in guilds.ids.keys():
      if guilds[member.guild.id].leaves and "leave" in list(guilds[member.guild.id]):
        await guilds[member.guild.id]["welcome"].send(
          r.choice( guilds[member.guild.id].leaves).format(str( member.id ))
        )

    await bot_log(f'left {member.id}', guild=member.guild, user=member)
  except Exception as ex:
    await response(author, f'Неизвестная ошибка бота {ex}')
    lines = ""
    for name, num, line in await rarse_exception(ex):
      lines += f"\n  {name} > {num}: {line}"
      await response(author, f"{name}\n > {num}: {line}")
    await bot_log(f'on_member_remove {ex}{lines}', guild=member.guild, user=member, type="error")

@client.event
async def on_message(message):
  global dialogfrom, dialogto
  if message.author == client.user:
      return
  
  if dialogfrom != '' and dialogto != '':
    try:
      if message.content != 'StopDialog':
        files = []
        for attach in message.attachments:
          files.append(await attach.to_file())
        if message.author == dialogto:
          await dialogfrom.send(content=message.content, files=files)
        elif message.author == dialogfrom:
          await dialogto.send(content=message.content, files=files)
        await bot_log(message.content, guild=member.guild, channel=message.channel, user=member, type="success")
      else:
        await dialogfrom.send('Подключение разорванно')
        dialogfrom, dialogto = '', ''
        await bot_log(message.content, guild=message.guild, channel=message.channel, user=message.author, cmd=0, type="success")
    except AttributeError:
      dialogfrom = ''
      dialogto = ''
  if message.author != dialogfrom:
    try:
      if guilds:
        res, guild = await guilds.execute_cmd(message, globals())
        if not res[0]:
          await bot_log(message.content, guild=message.guild, channel=message.channel, user=message.author, cmd=res[1], type="error" if res[1] else "success")
      else:
        await response(message, 'Используй эту команду позже, я не прошел инициализацию')
    except Exception as ex:
      await response(message, f'Неизвестная ошибка бота {ex}')
      lines = ""
      for name, num, line in await rarse_exception(ex):
        lines += f"\n  {name} > {num}: {line}"
        await response(author, f"{name}\n > {num}: {line}")
      await bot_log(message.content+str(ex)+lines, guild=message.guild, channel=message.channel, user=message.author, cmd=1, type="error")

while True:
  if replit:
    th(target=keep_alive).start()
  try:
    client.run(token, reconnect=None)
    break
  except:
    print(f"{Fore.YELLOW}\nBLOCKED BY RATE LIMITS\nRESTARTING NOW")
    popen(['python','main.py','&&','kill','1'])