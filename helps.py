import os, disnake as discord, io, traceback as tb, sys
import random, math
from linecache import getline

from numpy import *
from matplotlib import pyplot as plt


def bot_command(firstname: str, perms: dict):

  def decorator(func):

    async def wrapper(obj, gl, cmd, perm, *func_args, **kwargs):
      debug = gl.get("debug")

      a = None
      zero_arg = False
      cmd_perm = 0
      try:
        a = cmd[0]
      except IndexError:
        if 0 in perms.keys():
          zero_arg = True
        else:
          return await error(obj, firstname, 'null', 1)

      if perm == -2:
        return await error(obj, firstname, 'perm')
      elif a in perms.keys():
        cmd_perm = perms[cmd[0]]
      elif zero_arg:
        cmd_perm = perms[0]
      elif "" in perms.keys():
        cmd_perm = perms[""]
      else:
        return await error(obj, firstname, 'perm')

      if not (perm <= cmd_perm and perm > -1 or cmd_perm == -1):
        return await error(obj, firstname, 'perm')
      try:
        if len(cmd) > 0 or zero_arg:
          return await func(obj, gl, cmd, perm, *func_args, **kwargs)
        else:
          return await error(obj, firstname, 'null', 1)
      except Exception as ex:
        await error(obj, firstname, 'unknow', 1, com=ex if len(str(ex)) < 2000 else f'{ex[:2000]} ...')
        if debug:
          for frame in tb.extract_tb(ex.__traceback__)[1:]:
            num = frame.lineno
            name = frame.filename
            line = getline(name, num).strip()
            await response(obj, f"{name}\n > {num}: {line}")
        return 1

    return wrapper

  return decorator


async def check_arg(obj, name: str, args: list, i: int, arg: str, com=""):
  if len(args) > 0:
    if args[i] == arg:
      return True
  else:
    await error(obj, name, 'null', arg=i, com=com)
  return False


async def clear_console():
  if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
    os.system('clear')
  else:
    os.system('cls')


async def error(obj, name: str, err: str, i: int = 0, com: str = ""):
  errs = {
    'unknow': f'Неизвестная ошибка команды {name}:\n    Аргумент {i}: {com}.',
    'null': f"Ошибка при указании команды {name}:\n    Аргумент {i}: Отсутствует, используй {name} help, чтобы лучше узнать как использовать команду.",
    'wrong': f"Ошибка при указании команды {name}:\n    Аргумент {i}: Неправильный, используй {name} help, чтобы лучше узнать как использовать команду.",
    'perm': f"Ошибка при указании команды {name}:\n    Аргумент {i}: Не хватает прав на выполнение команды.",
    'nouser': f"Ошибка при указании команды {name}:\n    Аргумент {i}: Пользователь или канал не найден.",
    'nofile': f"Ошибка при указании команды {name}:\n    Аргумент {i}: Файл не найден.",
    'norole': f"Ошибка при указании команды {name}:\n    Аргумент {i}: Роль не найдена.",
  }
  await response(
    obj, f"{errs[err]}\n{com}" if com and err != "unknow" else errs[err])
  return 1


async def split_text(text, chunk_size=2000):
  return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


async def parseID(target: str):
  res = target.replace("<", "").replace("!", "").replace("£", "").replace("#", "").replace("@", "").replace("&", "").replace(">", "")
  return res


async def response(obj, text: str, files: list = []):
  if obj:
    if hasattr(obj, "channel"):
      return await obj.channel.send(content=text, files=files)
    else:
      return await obj.send(content=text, files=files)


async def filename(name: str):
  count = 1
  if os.path.isfile(f"files/{name}"):
    name, ext = ".".join(name.split(".")[:-1]), name.split(".")[-1]
    while True:
      if not os.path.isfile(f"files/{name}{count}.{ext}"):
        name = f"{name}{count}.{ext}"
        break
      else:
        count += 1
  return name


async def find(gl: dict,
               id: int,
               users: bool = True,
               chnls: bool = True,
               msgs=None):
  try:
    if msgs:
      if hasattr(msgs, "text_channels"):
        try:
          for ch in msgs.text_channels:
            channel = await ch.fetch_message(id)
            break
        except (discord.errors.Forbidden, discord.errors.NotFound):
          pass
    if users:
      try:
        channel = await gl.get("client").fetch_user(id)
      except discord.errors.NotFound:
        pass
    if chnls:
      try:
        channel = await gl.get("client").fetch_channel(id)
      except discord.errors.NotFound:
        pass
    return channel
  except:
    pass


async def parse_exception(ex):
  global debug
  res = []
  if debug:
    for frame in tb.extract_tb(ex.__traceback__):
      num = frame.lineno
      name = frame.filename
      res.append([name,num,getline(name, num).strip()])
  return res


async def plot_func(width, height, function, obj):
  msg = await response(obj, "Просчитываю функцию...")
  x = linspace(-width / 2, width / 2, 1000)
  y = function(x)

  await msg.edit(content="Отрисовываю график...")
  fig, ax = plt.subplots()

  ax.plot(x, real(y), label='Real')
  if any(iscomplex(y)):
    ax.plot(x, imag(y), label='Imaginary')
    
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  ax.set_title('Отрисовка функции')
  ax.legend()
  plt.grid(True)

  await msg.edit(content="Сохраняю изображение...")
  img_io = io.BytesIO()
  plt.savefig(img_io, format='png')
  img_io.seek(0)

  return img_io, msg


async def parseTarget(obj,
                      gl: dict,
                      channels: dict,
                      target: str,
                      users: bool = True,
                      chnls: bool = True,
                      msgs=None):
  target = await parseID(target)
  mems = [mem for mem in obj.guild.members
          if not mem.bot] if obj.guild != None else None
  #bots = [ bot for bot in obj.guild.members if bot.bot ]

  if target == "me" and users:
    return obj.author
  elif target == "here" and chnls:
    if obj.guild:
      return obj.channel
    else:
      return obj.author
  elif target == "author" and users:
    return gl.get("author")
  elif target.split("=")[0] == "random" and users:
    if obj.guild:
      if mems:
        user = random.choice(mems)
        return user
    else:
      return obj.author

  elif channels != None and target in channels.keys() and chnls:
    return channels[target]
  else:
    return await find(gl, target, users=users, chnls=chnls, msgs=msgs)