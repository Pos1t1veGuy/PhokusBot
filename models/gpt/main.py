import os, openai

info = "Генератор ответов на вопросы"
help = "```nn gpt use (текст): Генерирует ответ по (текст)\n```\nГенератор ответов на вопросы, созданный OpenAI. В отличии от конкурента Bard, он генерирует более креативные и человечные ответы"

async def use(obj, gl:dict, cmd:list, perm: int, msg):
  text, type = "", 0
  if len(cmd) > 2:
    openai.api_key = os.getenv("OPENAI_KEY")
    if openai.api_key:
      prompt = " ".join(cmd[2:])

      chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=[
        {"role": "user", "content": prompt}
      ])
      text = chat_completion.choices[0].message.content
      type = 0
    else:
      text = "Не удалось загрузить API ключ openai"
      type = 1
  else:
    text = "Требуется дописать текст для генерации ответа"
    type = 1
  return text, [], type