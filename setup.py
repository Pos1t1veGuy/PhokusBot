import os

class Guilds:
  def __init__(self, guilds:list, white_list:list, black_list:list):
    self.guilds = guilds
    self.author = int(os.getenv("AUTHORID"))
    self.white_list = white_list
    self.black_list = black_list
    self.ids = {}
    for guild in self.guilds:
      setattr(self, guild.name, guild)
      self.ids[guild.id] = guild
      
  async def execute_cmd(self, obj, globs:dict):
    cmd_name = obj.content.split(" ")[0]
    perm = await self.get_perm(obj, obj.guild)
    ctx = obj.content.split()[1:]

    if cmd_name in self.main.commands:
      res = await self.main.commands[cmd_name](obj, globs, ctx, perm if perm == 0 else -1)
      return [0, res], self.main.prefix

    for guild in self.guilds:
      if obj.guild != None:
        if guild.id == obj.guild.id:
          if cmd_name in guild.commands.keys():
            res = await guild.commands[cmd_name](obj, globs, ctx, perm)
            return [0, res], guild.prefix
    return [1, 1], None

  async def get_perm(self, obj, guild, msg:bool=True):
    if msg:
      return await self.get_msg_perm(obj, guild)
    else:
      return await self.get_user_perm(obj, guild)
  
  async def get_msg_perm(self, obj, gld):
    if obj.author.id == self.author:
      return 0
    elif obj.author.id in self.black_list:
      return -2
    elif obj.author.id in self.white_list.keys():
      return self.white_list[obj.author.id]
    elif gld:
      for guild in self.guilds:
        if guild.id == gld.id:
          user = obj.guild.get_member(obj.author.id)
          for role in user.roles:
            if role.id in guild.roles:
              return guild.roles[str(role.id)]
            
    return -1
  async def get_user_perm(self, author, gld):
    if author.id == self.author:
      return 0
    elif author.id in self.white_list.keys():
      return self.white_list[author.id]
    elif gld:
      for guild in self.guilds:
        if guild.id == gld.id:
          user = gld.get_member(author.id)
          for role in user.roles:
            if role.id in guild.roles:
              return guild.roles[str(role.id)]
            
    return -1

  def keys(self):
    return self.ids.keys()
  def values(self):
    return self.guilds.values()
  def items(self):
    return self.ids.items()
    
  def __dict__(self):
    return self.ids
  def __getitem__(self, i):
    return self.ids[i]
  def __list__(self):
    return self.guilds
  def __iter__(self):
    return iter(self.guilds)

class guild:
  def __init__(self, globs:dict, id:int, prefix:str, name:str,
               channels:dict={},
               welcomes:list=[],
               leaves:list=[],
               roles:list={},
               bans:list=[],
               kicks:list=[],
               unbans:list=[],
               helps:dict={},
               welcome_role:id=None
              ):
    self.name = name
    self.id = id
    self.channels = channels
    self.prefix = prefix
    
    self.roles = roles
    self.welcomes = welcomes
    self.leaves = leaves
    self.bans = bans
    self.kicks = kicks
    self.unbans = unbans
    self.helps = helps
    self.welcome_role = welcome_role
    
    self.commands = {}
    self.get_commands(globs)
  
  def get_commands(self, globs:dict):
    self.commands = {
      "_".join(cmd.split("_")[1:]) : globs.get(cmd) for cmd in globs if cmd.split("_")[0] == self.prefix
    }
    for k, v in self.commands.items():
      setattr(self, k, v)
      
  def __getitem__(self, i):
    return self.channels.keys()[i]
  def __list__(self):
    return self.channels.keys()