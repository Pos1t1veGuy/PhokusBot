def parse_lists():
  bl, wl = os.getenv("BLACK_LIST"), os.getenv("WHITE_LIST")

  white_list, black_list = {}, []

  if wl:
    white_list = {
      int(user.split(":")[0]) : int(user.split(":")[1])
      for user in wl.split(";") if wl != '.'
    }
  if bl:
    black_list = [
      int(user) for user in bl.split(";") if bl != '.'
    ]
  return black_list, white_list

def guilds_json_init(guilds_base: str):
  if os.path.isfile("guilds.json"):
    raw = json.load(open("guilds.json","r"))
    gindex = [
      raw.index(gld) for gld in raw if gld["name"]=="main"
    ]
    if gindex:
      raw[gindex[0]] = json.loads(guilds_base)[0]
    else:
      raw = [ json.loads(guilds_base)[0], *raw ]
    json.dump(raw, open("guilds.json","w"), ensure_ascii=False, indent=2)

def init_cfg(BotFiles: list, BotDirs: list):
  for dir in BotDirs:
    if not os.path.isdir(dir):
      os.mkdir(dir)
      print(f"Инициализировал {dir}")
  for file, wrt in BotFiles.items():
    if not os.path.isfile(file):
      open(file, "w").write(wrt)
      print(f"Инициализировал {file}")


import os, sys, json

from subprocess import Popen as popen
from colorama import init as colorama_init, Fore
from pytz import timezone, exceptions as tzexc
from itertools import cycle
from dotenv import load_dotenv
colorama_init()

replit = False # Opens Flask server to make bot always alive ( you must send "ping" requests to bot url in "webview" )

if not replit:
  load_dotenv()

token = os.getenv("TOKEN")     # Bot token
author = os.getenv('AUTHORID') # Author ID ( getting higher permission to user )

cmdLogger = 'botcmd.log'      # Command log file
eventLogger = 'bot.log'       # Event log file
logmsg = '[{}] ({},{},{}) {}' # Log message ( use "{}" for format to time, guild name, channel name, user name, message content )

sublibs = [   # Main libraries
  "commands", 
  "setup",    
  "helps",    
] + [         # Custon user libraries
]

status = cycle([ # Bot status "playing"
  'help, чтобы узнать мои команды',
  'Minecraft'
])


if not token:
  print(f"{Fore.RED}Ошибка инициализации: Не определен токен бота дискорд, требуется создать переменную окружения TOKEN или изменить токен в коде{Fore.RESET}")
  if replit:
    popen(['kill', '1'])
  else:
    sys.exit()

try:
  tz = timezone(os.getenv("TIMEZONE"))
except tzexc.UnknownTimeZoneError:
  print(f"{Fore.YELLOW}Ошибка инициализации: Не определена pytz.timezone, неизвестная зона. По умолчанию взято время с хоста. Требуется создать переменную окружения TIMEZONE или изменить таймзону в коде{Fore.RESET}")
  tz = None

guilds = None

dialogfrom = ""
dialogto = ""

cfg_base = json.dumps({
  "logging": True, "wake up": True, "debug": True
})
guilds_base = json.dumps([
  {
    "id": None,
    "name": "main",
    "prefix": "main",
    "helps": {
        "0": "**help 0**\nПривет! Ты попал на страницу help 0. Мои команды отличаются от сервера к серверу, некоторые не работают на других серверах. Можешь использовать help на серверах, чтобы узнать все уникальные команды и использовать help cmds, чтобы узнать межсерверные команды и информацию.\n**Короче, просто используй help 1, чтобы открыть слейдующую страницу поддержки 1 или, если страницы 1 нет, то ты можешь использовать help cmds, чтобы получить команды по умолчанию**",
        "cmds": """**Общие команды**
Все команды имеют аргумент второй help, там объяснсяется подробно как используется каждая команда, в скобках указан минимальный уровень доступа для использования команды (подробнее в help access)
```
1.  help -     (-1) Выдает справку по указанному имени
2.  clear -    (0)  Удаляет n последних сообщений в канале
3.  nn -       (-1) Работа со встроенными нейросетями
4.  trans -    (-1) Переводчик текста
5.  files -    (0)  Манипуляция файловой системой бота
6.  perm -     (-1) Вывол текущего уровня доступа
7.  plt -      (0)  Построение графика геометрической функции
8.  init -     (0)  Инициализизует базовые файлы бота
9.  reload -   (0)  Перезагрузка бота
10. dialog -   (0)  Диалог с пользователями от имени бота
11. send -     (0)  Отправляет сообщение от имени бота
12. execute -  (0)  Выполняет строку python внутри функции
13. ping -     (-1) Команда-попугай для тестирования бота
14. log -      (0)  Управление системой логирования
15. shutdown - (0)  Выключение бота
```
Это не все мои команды, есть еще уникальные для каждого сервера. Чтобы узнать их пишите help cmds на других серверах""",
        "access": """**Уровни доступа**
Для использования команд бота нужно иметь необходимый уровень доступа.
**Уровень доступа** - это число от -1 до бесконечности
**Уровень -1** значит общий доступ, то есть доступ по умолчанию доступный всем.
**Уровни от 0 до бесконечности** значат уже особый доступ, 0 - максимальный (уровень администратора), далее 1, он чуть слабее, 2 - тоже, ну и тд.
Ваш уровень доступа вы можете узнать комндой perm. Если вы взаимодействуете со мной в лс, то у вас будет всегда уровень -1, на моих серверах ваш уровень может быть уже в пределе от 0 до бесконечности.
"""
      }
  }
], ensure_ascii=False, indent=2)

BotFiles = {
  "roles.json": "{}",
  "config.json": cfg_base,
  "guilds.json": guilds_base,

  cmdLogger: "",
  eventLogger: "",
}
BotDirs = [
  "files",
  "models"
]

black_list, white_list = parse_lists()
init_cfg(BotFiles, BotDirs)
guilds_json_init(guilds_base)

cfg = json.load(open("config.json", "r"))
  
logging = cfg["logging"]
wakeup = cfg["wake up"]
debug = cfg["debug"]
guilds_cfg = json.load(open("guilds.json", "r"))

if not wakeup:
  print(f"{Fore.RED}Включение отклонено, измени параметр 'wake up' в config.json{Fore.RESET}")
  if replit:
    popen(['kill', '1'])
  else:
    sys.exit()