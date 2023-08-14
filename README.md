# PhokusBot
Bot for discord server

PhokusBot is a highly customizable discord bot.


# That's what i can
1. Tailor events and commands for each server
2. Correctly log each event
3. Bot am easily customized for the user from several configuration files
4. Bot have built-in neural networks


# How To Use Me
Install bot first
## Installing
You need to clone repository:
```
git clone https://github.com/Pos1t1veGuy/PhokusBot
```
After that you must install every requirements, go to my installed directory:
```
cd PhokusBot
```
And install requirements using pip:
```
pip install -r requirements.txt
```
And turn me on execute main.py using python 3:
For MacOS/Linux:
```
python3 main.py
```
For Windows:
```
main.py
```
You must specify the token of your discord bot in .env, check Bot Setup.
If bot has some warnings, it will printed in yellow in console.
## Using
Bot has default customized guild 'main' with prefix 'main' and some commands ( this guild usig for every server and in private ), after turning on the bot you can use 'help' for absolute help or 'help cmds' for help with commands. For example you can try 'ping' and bot should answer 'pong'. You can change main guild in commands.py.

If you have problems with bot language use 'trans en (copyed message)'.


# Bot Setup
First you need to configure the .env file, it contains secrets, like a bot token. There are required and optional variables.
The bot is configured in special config.py, config.json, .env files. First, let's talk about env:

## env
And in env let's talk about the token for the bot:

### Bot Token
```
# .env
TOKEN=.
```
At the moment, it is mandatory to configure only the bot token, it is needed to manage the bot.
To get it, you need to go to https://discord.com/developers/applications and, if there is a bot, then get the previously saved key, or re-create it on the page of your application, else create new application like "PhokusBot".

To do this, find and click on 'Bot' in the panel on the left. A window should appear on the right and under the 'Build-A-Bot' heading there should be a 'Reset Token' button, after clicking the token will change, and at that moment you can copy and save it.
```
# .env
TOKEN=BO0O0O0O0O0O0O0O0T.TO0O0O0O0O0OO0O0O0KEN
```
The entry should look something like this, it should not contain spaces, otherwise there will be an error.

### Black List & White List
```
# .env
WHITE_LIST=.
BLACK_LIST=.
```
In these variables, you can configure access to the bot through commands in discord.

In BLACK_LIST, you need to specify discord user IDs through ';', the entry should look like this:
```
# .env
BLACK_LIST=12345678;87654321
```
Blacklisted people will not have access to commands at all.

As for WHITE_LIST, here you need to specify the discord user IDs with ';', but you also need to add a permission level, with ':' after every ID. For example:
```
# .env
WHITE_LIST=12345678:-1;87654321:1
```
Read more about permission levels below...

### Time Zone
The time zone setting is needed mainly for correct logging, there is a TIMEZONE variable for this:
```
# .env
TIMEZONE=.
```
There you need to specify a string for the pytz.timezone object, like:
```
# .env
TIMEZONE=Europe/Moscow
```
### Author ID
Setting the author ID is needed to issue the maximum level of rights, despite the black and white lists:
```
#.env
AUTHORID=.
```
You need to specify the discord user ID, the entry should look something like this:
```
#.env
AUTHORID=12345678
```

### OpenAI Key
Requires several built-in neural networks to work:
```
#.env
OPENAI_KEY=.
```
You need to specify the token at https://platform.openai.com/account/api-keys, if it is not there, you can leave '.':
```
#.env
OPENAI_KEY=sk-sdfghjkljhgfddfghjfghgfjfjghjgjgh
```

## config.py
Setting variables in the main code:
### replit
Must contain bool.
If True, opens a local Flask server on port 8080. Needed if the bot is used on replit to set up persistent activity for free. To do this, you need to send any requests ( for example ping ) to the address from the webview of the replit window. ( For the window to appear, you need to run the application )

### cmdLogger, eventLogger
Must contain str.
These are the names of the log files for tracking commands and events, respectively. They appear in the directory of the main.py file when absent.

### logmsg
Must contain str.
The line for outputting the log to the file and the console, curly braces are replaced by time, guild name, channel name, user name, message content in the code.

### sublibs
Must contain list.
This is a list of user-defined libraries that are connected, such as libraries with commands. It has a default structure:
```
sublibs=[
  # Main libraries
] + [
  # User libraries
]
```
Modules are included in the code automatically when added to the list. To make it clearer to parse the code, the main libraries ( which are undesirable to be deleted ) and user libraries are separated.

### status
Must contain itertools.cycle.
This is an endless list of bot statuses, they are updated every 60 seconds.

## config.json
Has only 3 items:
```
'logging' (bool) - enabling and desabling log system,
'wake up' (bool) -  if true bot can not start,
'debug' (bool) - if true bot should view full error tranceback if discord
```


# Guilds Setup
Each guild ( I mean the server, but everywhere in the code and in this text the server is called a guild ) can be described in guids.json. There you can create a welcome message, a farewell message, unique commands, and similar settings.
Each guild has a 'name', 'id' and 'prefix'. 'name' is an arbitrary name, it has little effect. 'id' is the ID of the discord server. 'prefix' is the prefix of functions in the code that will only be used in this guild.

By the way, bot has default customized guild 'main' with prefix 'main' and some commands ( this guild usig for every server and in private ), after turning on the bot you can use 'help' for absolute help or 'help cmds' for help with commands. For example you can try 'ping' and bot should answer 'pong'. You can change main guild in commands.py.

## Let's start with setting commands
Functions must be asynchronous, that is, when creating, you need to use the 'async def' construct, and not just 'def'
If our guild 'prefix' is 'test', then the function name should look like this:

### Creating Function
```
from helps import bot_command

@bot_command('ping', {})
async def test_ping(obj, gl, cmd, perm):
  return 0
```
This code creates a 'ping' function that the bot receives from the user's discord. (Each function must return 0 if the command completed without errors and 1 if an error occurred)

First, importing 'bot_command' from 'helps.py' is required, this decorator helps set up the command, more on that later.
Secondly, we attach a decorator to the 'ping' function, the first argument must be the name of the function, i.e. the string 'ping'.
Thirdly, the 'test_ping' function takes 4 disnake.Message arguments, main.py globals(), a list of arguments ( strings ) without the first argument ( function name, because it is not needed ), the command's user access level.

### Setting permissions
```
from helps import bot_command

@bot_command('ping', {"help":-1, "":1, 0:0})
async def test_ping(obj, gl, cmd, perm):
  return 0
```
Для 'ping help' требует уровень -1 от пользователя.
Для 'ping ( аргумент )' требует уровень 1, для всех аргументов, кроме зарегестрированных ( то есть все, кроме help )
Для 'ping' требует уровень 0 ( второго аргумента нет )

### Creating  Response
```
from helps import bot_command, response, error

@bot_command('ping', {"help":-1, "":1, 0:0})
async def test_ping(obj, gl, cmd, perm):
  if len(cmd) > 0:
    if cmd[0] == 'help':
      await response(obj, 'help page')
      return 0
    else:
      return await error(obj, 'ping', 'wrong', 1, com='wrong argument')
  else:
    await response(obj, 'pong')
    return 0
  return 1
```
First, if there is no argument ( 'ping' is specified), then the bot replies with 'pong'.
Secondly, if there is a 'help' argument ( 'ping help' is specified), then the bot will respond with 'help page'.
Third, if the argument is not 'help', then an error is output for the 'ping' command and argument 1 with the comment 'wrong argument'.

The response function sends a message if obj != None and returns the sent message.
The error function generates an error message using a message object, a string with the function name, error type, argument number, and a comment. The types of errors are listed below:
```
'unknow' - Command argument is unknow,
'null' - No command argument,
'wrong' - Command argument is wrong,
'perm' - lack of execution permissions,
'nouser' - User is not defined,
'nofile' - File is not defined,
'norole' - Role is not defined
```

## Next you need to set up guilds.json
После настройки основных параметров бота можно настроить второстепенные:
```
'channels' (dict) - Сhannel names by discord channel id ( name:id ),
'welcomes' (list) - Messages that are issued when a user joined ( "{}" will format to user name ),
'leaves' (list) - Messages that are issued when a user left ( "{}" will format to user name ),
'roles' (list) - Hierarchy of roles from strongest to weakest,
'bans' (list) - Messages that are issued when a user is banned ( "{}" will format to user name ),
'kicks' (list) - Messages that are issued when a user is kicked ( "{}" will format to user name ),
'unbans' (list) - Messages that are issued when a user is unlocked ( "{}" will format to user name ),
'helps' (dict) - Help pages for command 'help',
'welcome_role' (int) - ID of the role given to new user by the bot
```
These are all available settings for the guild in guilds.json.


# Users Access Levels
By default, each user has an access level of -1, the public level. The maximum access level is 0, administrator level. Further 1, 2, 3 and further to infinity levels below.
