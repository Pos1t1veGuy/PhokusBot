import os
import disnake as discord
import random
import json
import shutil as sh
import requests as rq
import traceback as tb
import importlib as il

from subprocess import Popen as popen
from asyncio import sleep
from translate import Translator
from linecache import getline

from helps import *


@bot_command('nn', {"help": -1, "": -1, "list": -1})
async def main_nn(obj, gl: dict, cmd: list, perm: int):
  if cmd[0] == "help":
    await response(obj, "Синтаксис:```\n  nn (имя сети) help\n  nn (имя сети) use\n  nn list\n```Описание:\n  Работа со встроенными нейросетями. \n**help** вывод информации об (имя сети), можно оставить третий аргумент функции пустым\n**use** Передает дальнейшие строчные аргументы или встроенные файлы в нейросеть на обработку для выдачи результата\n**list** показывает существующие сети. Команда доступна всем")
    return 0
  elif cmd[0] == "list":
    models_dirs = [
      dir for dir in os.listdir("models") if os.path.isdir(f"models/{dir}")
    ]
    models = ""

    for i, model in enumerate(models_dirs):
      try:
        info = "AI модель"
        module = il.import_module(f"models.{model}.main")
        info = module.info
        models += f"{i+1}.{ ' ' if i+1 in range(0,10) else '' } { model } - { info }\n"
      except ImportError:
        pass

    await response(obj, f"AI модели:\n```{models if models else 'Отсутствуют'}```")
    return 0
  else:
    models = [
      dir for dir in os.listdir("models") if os.path.isdir(f"models/{dir}")
    ]
    if cmd[0] in models:
      if len(cmd) > 1:
        try:
          module = il.import_module(f"models.{cmd[0]}.main")
          use, help = module.use, module.help
        except ImportError:
          return await error(obj, "nn (сеть)", "unknow", 2, com="Не удалось импортировать сеть")
        if cmd[1] == "use":
          msg = await response(obj, "Загружаю ответ...")
          text, file, type = await use(obj, gl, cmd, perm, msg)
          for i, t in enumerate(await split_text(text)):
            if file and not i:
              await response(obj, t, files=[file])
            else:
              await response(obj, t)
          await msg.delete()
          return type
        elif cmd[1] == "help":
          await response(obj, help)
          return 0
        else:
          return await error(obj, "nn (сеть)", "wrong", 2, com="Требуется указать (use/help)")
      else:
        return await error(obj, "nn (сеть)", "null", 2, com="Требуется указать (use/help)")
    else:
      return await error(obj, "nn (сеть)", "wrong", 1, com="Модель не найдена, используй nn list для получения списка моделей")
  return 1


@bot_command("plt (ширина) (высота) (функция)", {"help": 0, "": -1})
async def main_plt(obj, gl: dict, cmd: list, perm: int):
  if cmd[0] == "help":
    await response(obj, "Синтаксис:```\n  plt (ширина графика) (высота графика) (функция)\n```Описание:\n  Построение графика y = (функция) на графике, функция должна соблюдать синтаксис python, импорт библиотек: numpy as np; import math; import random, учтите что функция регистрируется как lambda x: (ваш код), график будет выслан как png файл, чтобы указать мнимую единицу - 1j. Комаsнда доступна всем")
    return 0
  else:
    try:
      x = int(cmd[0])
      if not x > 0 and x <= 50:
        raise ValueError("")
    except ValueError:
      await error(obj, "plt (ширина) (высота) (функция)", 'wrong', 1, com="Требуется указать ширину графика, число от 0 до 50")
      return 1
    if len(cmd) > 1:
      try:
        y = int(cmd[1])
        if not y > 0 and x <= 50:
          raise ValueError("")
      except ValueError:
        await error(obj, "plt (ширина) (высота) (функция)", 'wrong', 2, com="Требуется указать высоту графика, число от 0 до 50")
        return 1
      if len(cmd) > 2:
        func = eval(f"lambda x: {' '.join(cmd[2:])}")
        file, msg = await plot_func(x, y, func, obj)
        await msg.edit(content=f"График y = {cmd[2]}", files=[discord.File(file, filename="plt.png")])
        return 0
      else:
        await error(obj, "plt (ширина) (высота) (функция)", 'null', 3, com="Требуется указать функцию python y = lambda x: (ваша функция)")
    else:
      await error(obj, "plt (ширина) (высота) (функция)", 'null', 2, com="Требуется указать ширину графика, число от 0 до 50")
  return 1


@bot_command("perm (цель)", {"help": -1, 0: -1, '': 1})
async def main_perm(obj, gl: dict, cmd: list, perm: int):
  guilds = gl.get("guilds")
  if len(cmd) == 0:
    return await main_perm(obj, gl, ["me"], 0)
  if cmd[0] == "help":
    await response(obj, "Синтаксис:```\n  perm (цель)\n```Описание:\n  Вывод текущего уровня доступа (цель). (цель) модно не указывать, тогда будет выведен ваш уровень доступа. Команда доступна всем")
    return 0
  else:
    if len(cmd) > 0:
      target = await parseTarget(obj, gl, None, cmd[0], chnls=False)
    else:
      target = obj.author
    if target:
      await response(obj, f"Текущий уровень доступа {target.name} {await guilds.get_perm(target,obj.guild,msg=False)}")
      return 0
    else:
      return await error(obj, "perm (цель)", "nouser", 1, com="Требуется указать пинг, имя пользователя или сокращение (me, author, random)")
  return 1


@bot_command("files (ls/upload/download/remove/net)", {
  "help": -1,
  "ls": 0,
  "upload": 0,
  "download": 0,
  "remove": 0,
  "net": 0
})
async def main_files(obj, gl: dict, cmd: list, perm: int):
  if len(cmd) == 0:
    return await main_files(obj, gl, ["ls"], perm)
  if cmd[0] == "help":
    await response(obj, "Синтаксис:```\n  files ls (папка1) (папка2 в папке1) ...\n  files upload (файл1) (файл2) ...\n  files download (файл1) (файл2) ...\n  files remove (файл1/папка1) (файл2/папка2) ...\n  files net (файл) (ресурс)\n```Описание:\n  Манипуляция файловой системой бота.\n**ls** показывает все папки и файлы, по умолчанию это корневая, но при указании (папка1) будут выводиться файлы из этой папки, если она существует, так же и с последующими.\n**upload** загружает все прикрепленные файлы, по желанию можно указать имена этих файлов в (файл1) (файл2) и тд.\n**download** скачивает (файл1), (файл2) и тд вам в чат, если файлы существуют.\n**remove** удаляет файл или папку в аргументах (файл1/папка1), (файл2/папка2) и тд, если они существуют.\n**net** скачивает файл с (ресурс) и сохраняет как (файл).\nТребуется 0 уровень доступа")
    return 0
  elif cmd[0] == "ls":
    join = os.path.join
    ls = os.listdir("files/" + "/".join(cmd[1:]))
    files = [file for file in ls if os.path.isfile(join("files", file))]
    dirs = [dir for dir in ls if os.path.isdir(join("files", dir))]
    if len(files) == 0:
      files = ["Отсутствуют"]
    if len(dirs) == 0:
      dirs = ["Отсутствуют"]

    if len(dirs) > len(files):
      more, less = dirs, files
      space = max(len(m) for m in more) + 1
      res = f"```    Папки:{' ' * (space-6)} Файлы:"
    else:
      more, less = files, dirs
      space = max(len(m) for m in more) + 1
      res = f"```    Файлы:{' ' * (space-6)} Папки:"

    for i in more:
      j = more.index(i) + 1
      num = f"{j}. " + (" " if j in range(0, 10) else "")
      res += f"\n{num}{i}{' '*(space-len(i))} "
      if len(less) >= more.index(i) + 1:
        res += less[more.index(i)]
    res += "```"

    await response(obj, res)
    return 0
  elif cmd[0] == "upload":
    names = []
    if len(cmd) > 1:
      for name in cmd[1:]:
        names.append(name)
    for file in obj.attachments:
      i = obj.attachments.index(file)
      if len(names) >= i + 1:
        name = names[i]
      else:
        name = file.filename
      name = await filename(name)

      await file.save(f"files/{name}")
      await response(obj, f"Сохранил файл {i+1} как {name}")
    await response(obj, f"Сохранил { len(obj.attachments) } файлов")
    return 0
  elif cmd[0] == "download":
    if len(cmd) > 1:
      files = []
      for file in cmd[1:]:
        if os.path.isfile(f"files/{file}"):
          files.append(discord.File(f"files/{file}"))
        else:
          return await error(obj, "files download (имена)", "nofile", 1)
      await response(obj, f"Файлов {len(files)}", files=files)
      return 0
    else:
      return await error(obj, "files download (имена)", "null", 1, com="Требуется указать имя/имена файлов, загруженных в бота")
  elif cmd[0] == "remove":
    if len(cmd) > 1:
      for i in cmd[1:]:
        if os.path.exists(f"files/{i}"):
          if os.path.isfile(f"files/{i}"):
            os.remove(f"files/{i}")
          elif os.path.isdir(f"files/{i}"):
            sh.rmtree(f"files/{i}")
          await response(obj, f"Удалил {i}")
          return 0
        else:
          return await error(obj, "files", "nofile", 1)
    else:
      return await error(obj, "files download (имена)", "null", 1, "Требуется указать имя/имена файлов, загруженных в бота")
  elif cmd[0] == "net":
    if len(cmd) > 1:
      name = await filename(f"files/{cmd[1]}")
      if len(cmd) > 2:
        link = " ".join(cmd[2:])
        open(name, "wb").write(rq.get(link).content)
        await response(obj, f"Скачал файл и сохранил под именем { name }")
      else:
        return await error(obj, "files net (файл) (ресурс)", "null", 2, com="Требуется указать ресурс, с которого будет скачан файл")
    else:
      return await error(obj, "files net (файл) (ресурс)", "null", 2, com="Требуется указать имя, под которым будет сохранен скачанный файл")
  return 1


@bot_command("trans (язык) (текст)", {"help": -1, "": -1})
async def main_trans(obj, gl: dict, cmd: list, perm: int):
  if cmd[0] == "help":
    await response(obj, f"Синтаксис:```\n  trans (язык) (текст)\n```Описание:\n  Команда-переводчик, переводит (текст) на (язык), (язык) это сокращение из двух анлийских букв ( например ru, en ). Команда доступна всем"
    )
    return 0
  else:
    trans = Translator(to_lang=cmd[0])
    if len(cmd) > 1:
      inp = ' '.join(cmd[1:])
      text = trans.translate(inp)
      if text == f"'{cmd[0].upper()}' IS AN INVALID TARGET LANGUAGE . EXAMPLE: LANGPAIR=EN|IT USING 2 LETTER ISO OR RFC3066 LIKE ZH-CN. ALMOST ALL LANGUAGES SUPPORTED BUT SOME MAY HAVE NO CONTENT":
        return await error(obj, "trans (язык) (текст)", "wrong", 1, com="Требуется указать код языка, НА который будет переведен текст. Возможно этот код существует, но не зарегестрирован в google translate")
      await response(obj, f'Перевел ваш текст:\n{ inp } => { text }')
      return 0
    else:
      return await error(obj, 'trans (язык) (текст)', 'null', 2, com="Требуется указать текст для перевода на другой язык")
  return 1


@bot_command("shutdown", {"help": -1, 0: 0})
async def main_shutdown(obj, gl: dict, cmd: list, perm: int):
  cmd_perm = 0
  count = 1
  debug = gl.get("debug")
  if len(cmd) > 0:
    if cmd[0] == "help":
      await response(obj, "Синтаксис:```\n  shutdown (целое 300 > n > 0) \n```Описание:\n  Отключение бота через n секунд, n можно не указывать, по умолчанию n=1. Требуется 0 уровень доступа")
      return 0
    else:
      try:
        count = int(cmd[0])
      except ValueError:
        pass
  if count in range(0, 301):
    await response(obj, f"Начну отключение через {count} секунд")
    await sleep(count)
    gl["wakeup"] = not gl["wakeup"]
    oldjson = json.load(open("config.json", "r"))
    oldjson["wake up"] = bool(gl["wakeup"])
    json.dump(oldjson, open("config.json", "w"))
    await response(obj, "Отключаюсь...")
    await gl.get("client").close()
    if replit:
      popen(['kill', '1'])
    else:
      sys.exit()
    return 0
  else:
    return await error(obj, "shutdown (время)", "wrong", 1, com="Требуется указать количество секунд, серез которое будет выполнено отключение. Число долдно быть меньше 300 и больше 0")
  return 1


@bot_command("log (mode/re/clear)", {
  "help": -1,
  "mode": 0,
  "re": 0,
  "clear": 0
})
async def main_log(obj, gl: dict, cmd: list, perm: int):
  if cmd[0] == "help":
    await response(obj, "Синтаксис:```\n  log mode\n  log re\n  log clear\n```Описание:\n  Настройка системы логирования.\n**mode** выводит текущий режим логирования (включено/выключено).\n**re** меняет редим на противоположный с текущего (включено/выключено).\n**clear** очищает все логи.\nТребуется 0 уровень доступа")
    return 0
  elif cmd[0] == "mode":
    logging = gl.get("logging")
    await response(obj, f'Система логирования сейчас {"отключена" if not logging else "включена"}')
  elif cmd[0] == "re":
    gl["logging"] = not gl["logging"]
    oldjson = json.load(open("config.json", "r"))
    oldjson["logging"] = bool(gl["logging"])
    json.dump(oldjson, open("config.json", "w"))

    await response(
      obj,
      f'Теперь система логирования {"отключена" if not gl["logging"] else "включена"}'
    )
  elif cmd[0] == "clear":
    open("cmdlog.txt", "w")
    open("log.txt", "w")
    await response(obj, 'Почистил лог')
  return 0


@bot_command("reload", {"help": -1, 0: 0})
async def main_reload(obj, gl: dict, cmd: list, perm: int):
  if len(cmd) > 0:
    if cmd[0] == "help":
      await response(obj, "Синтаксис:```\n  reload\n```Описание:\n  Перезагрузка бота. При перезагрузке бот обновляет команды и инициализируется как при запуске. Требуется 0 уровень доступа")
      return 0
  else:
    msg = await response(obj, "Начинаю перезагрузку...")
    await gl.get("ginit")()
    await msg.edit(content="Перезагрузка окончена")
    return 0
  return 1


@bot_command("help", {"help": -1, "": -1, 0: -1})
async def main_help(obj, gl: dict, cmd: list, perm: int):
  guilds = gl.get("guilds")
  if len(cmd) > 0:
    if cmd[0] == "help":
      await response(obj, "И на что ты надеялся? help help? Ты серьезно?")
      return 0
    else:
      if obj.guild:
        if obj.guild.id in guilds.keys():
          if cmd[0] in guilds[obj.guild.id].helps:
            await response(obj, guilds[obj.guild.id].helps[cmd[0]])
            return 0

      if cmd[0] in guilds.main.helps:
        await response(obj, guilds.main.helps[cmd[0]])
        return 0
      else:
        return await error(obj, "help (страница)", "wrong", 1, com=f"Страница {cmd[0]} не найдена")
  else:
    return await main_help(obj, gl, ["0"], perm)
  return 1


@bot_command("execute", {"help": -1, "eval": 0, "exec": 0})
async def main_execute(obj, gl: dict, cmd: list, perm: int):
  if cmd[0] == "help":
    await response(obj, "Синтаксис:```\n  execute eval (код python)\n  execute exec (код python)\n```Описание:\n  Выполняет строку python внутри функции.\n**exec** просто выполняет код.\n**eval** выполняет код и возвращает результат. Требует 0 уровень доступа")
    return 0
  elif cmd[0] == "eval":
    try:
      for key, value in gl.items():
        globals()[key] = value
      res = eval(" ".join(cmd[1:]))
      if len(str(res)) < 3950:
        await response(obj, f"Использовал эту строку, возврат: {res}")
        return 0
      else:
        await response(obj, f"Использовал эту строку, возврат невозможен, тк он превышает лимит в 4,000 символов в сообщении")
    except Exception as ex:
      num = ex.__traceback__.tb_lineno
      line = getline(ex.__traceback__.tb_frame.f_code.co_filename, num).strip()
      await response(obj, f'Код вернул ошибку {ex}:\n > {num}: {line}')
  elif cmd[0] == "exec":
    try:
      exec(" ".join(cmd[1:]))
      await response(obj, "Использовал эту строку")
      return 0
    except Exception as ex:
      num = ex.__traceback__.tb_lineno
      line = getline(ex.__traceback__.tb_frame.f_code.co_filename, num).strip()
      await response(obj, f'Код вернул ошибку {ex}:\n > {num}: {line}')
  return 1


@bot_command("clear", {"help": -1, "": -1})
async def main_clear(obj, gl: dict, cmd: list, perm: int):
  if cmd[0] == "help":
    await response(obj, "Синтаксис:```\n  clear (целое n > 0)\n```Описание:\n  Удаляет n последних сообщений в вашем канале. Команда доступна всем, у кого есть разрешение изменять сообщения")
    return 0
  else:
    guilds = gl.get("guilds")
    if obj.guild:
      if obj.author.guild_permissions.manage_messages or obj.author.guild_permissions.administrator:
        try:
          count = int(cmd[0])
        except ValueError:
          return await error(obj, "clear (количество)", "wrong", 1, com= "Нужно указать количество сообщений для очистки в этом канале в виде числа")
        await obj.channel.purge(limit=count)
        await response(obj, f"Очистил {count} {'сообщение' if count == 1 else 'сообщения' if count in range(1, 5) else 'сообщений'}")
        return 0
      else:
        return await error(obj, "clear (количество)", "perm", 0, com="Требуется разрешение изменять сообщения")
    else:
      await response(obj, "Эту команду можно использовать только на сервере")
  return 1


@bot_command("send", {"help": -1, "": 0})
async def main_send(obj, gl: dict, cmd: list, perm: int):
  if cmd[0] == "help":
    await response(obj, "Синтаксис:```\n  send (ссылка на объект) (сообщение из любых символов)\n```Описание:\n  Отправляет сообщение от имени бота. (ссылка на объект) - это пинг канала или человека, ник человека или сокращение (me, here, author, сокращение канала, random). Требует 0 уровень прав")
    return 0
  else:
    guild = None if obj.guild == None else obj.guild.id
    guilds = gl.get("guilds")
    g = guild if guild in guilds.keys() else None
    target = await parseTarget(obj, gl, guilds[g].channels, cmd[0])
    files = [await i.to_file() for i in obj.attachments]
    if len(cmd) > 1:
      if target:
        await target.send(content=" ".join(cmd[1:]), files=files)
        return 0
      else:
        return await error(obj, "send (цель) (контент)", "nouser", 2)
    else:
      return await error(obj, "send (цель) (контент)", "null", 2, com="Требуется указать контент сообщения")
  return 1


@bot_command("dialog", {"help": -1, "": 0})
async def main_dialog(obj, gl: dict, cmd: list, perm: int):
  if cmd[0] == "help":
    await response(obj, "Синтаксис:```\n  dialog (ссылка на объект)\n```Описание:\n  Устанавливает dialog соединение с целью, вы пишете и вам отвечают. (ссылка на объект) - это пинг канала или человека, ник человека или сокращение (me, here, author, сокращение канала, random). Требует 0 уровень прав")
    return 0
  else:
    try:
      guild = None if obj.guild == None else obj.guild.id
      guilds = gl.get("guilds")
      g = guild if guild in guilds.keys() else None
      gl["dialogto"] = await parseTarget(obj, gl, guilds[g].channels, cmd[0])
      gl["dialogfrom"] = obj.author
      await response(obj, 'Успешно установил связь с целью, теперь любое ваше сообщение будет передано цели, чтобы закончить диалог StopDialog')
      return 0
    except discord.errors.HTTPException:
      return await error(obj, "dialog (цель)", "nouser", 1)
  return 1


@bot_command("init", {"help": -1, 0: 0})
async def main_init(obj, gl: dict, cmd: list, perm: int):
  if len(cmd) > 0:
    if cmd[0] == "help":
      await response(obj, "Синтаксис:```\n  init\n```Описание:\n  Инициализизует базовые файлы бота, создает новые при отсутствии. Требует 0 уровень доступа")
      return 0
  else:
    files, dirs = gl.get("BotFiles"), gl.get("BotDirs")
    for dir in dirs:
      if not os.path.isdir(dir):
        os.mkdir(dir)
        await response(obj, f"Инициализировал {dir}")
        print(f"Инициализировал {dir}")
    for file, wrt in files.items():
      if not os.path.isfile(file):
        open(file, "w").write(wrt)
        await response(obj, f"Инициализировал {file}")
        print(f"Инициализировал {file}")
    await response(obj, "Инициализация окончена")
    return 0
  return 1


@bot_command("ping", {"help": -1, 0: -1})
async def main_ping(obj, gl: dict, cmd: list, perm: int):
  if len(cmd) > 0:
    if cmd[0] == "help":
      await response(obj, "Синтаксис:```\n  ping\n```Описание:\n  Команда-попугай для тестирования бота, всегда отвечает pong. Команда доступна всем")
      return 0
  else:
    await response(obj, "pong")
    return 0
  return 1
