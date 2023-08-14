import os, openai, requests, io, disnake as discord

info = "Генератор изображений из слов"
help = "```nn dalle use (текст): Генерирует картинку по (текст)```\nГенератор изображений из слов, созданный OpenAI. Имеет ограничение в 1,000 символов и лишнее будет отрезать с конца"

async def use(obj, gl:dict, cmd:list, perm: int, msg):
  text, file, type = "", [], 0
  if len(cmd) > 2:
    openai.api_key = os.getenv("OPENAI_KEY")
    if openai.api_key:
      prompt = " ".join(cmd[2:])
      prompt = prompt[:1000] if len(prompt) > 1000 else prompt
      
      img = openai.Image.create(prompt=prompt, size="512x512")
      response = requests.get(img["data"][0]["url"])
      
      if response.status_code == 200:
        file = discord.File( io.BytesIO(response.content), filename="pic.png" )
        text = prompt
        type = 0
      else:
        text = "Не получилось скачать картинку с openai"
        type = 1
    else:
      text = "Не удалось загрузить API ключ openai"
      type = 1
  else:
    text = "Требуется дописать текст для генерации картинки"
    type = 1
  return text if len(text) < 100 else f'{text[:100]} ...', file, type