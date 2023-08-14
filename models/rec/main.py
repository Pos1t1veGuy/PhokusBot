import speech_recognition as sr
import pydub, sys, io, math

from pydub import AudioSegment as aus

info = "Конвертер звуков речи в текст"
help = "```nn rec use (язык): Конвертирует звуки речи в текст по языку (язык)\n```\nКонвертер звуков речи в текст, созданный Google ( Полное имя SpeechRecognition, модуль Python ). Принимает на вход аудио файлы распространенных форматов ( m4a, mp3, wav ) и возвращает текст по каждому прикрепленному файлу.\n(язык) - это короткий код, список кодов можно найти на ```https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages```\nили использовав сокращение из двух букв ( ru, en, de ), сокращение для некоторых популярных языков"


async def use(obj, gl: dict, cmd: list, perm: int, msg):
  fast_langs = {
    'ru': "ru-RU",
    'en': "en-US",
    'ja': "ja-JP",
    'de': "de-DE",
    'fr': "fr-FR",
    'po': "pl-PL",
    'be': "nl-BE",
    'cz': "cs-CZ",
    'it': "it-IT",
    'gr': "el-GR",
    'uk': "uk-UA",
    'be': "nl-BE",
    'cr': "hr-HR",
    'sv': "sv-SE",
    'no': "no-NO",
    'da': "da-DK",
    'ro': "ro-RO",
    'fi': "fi-FI",
  }
  text, type = "", 0

  if len(cmd) > 0:
    lang = fast_langs.get(cmd[2]) if cmd[2] in fast_langs.keys() else cmd[2]

    if not len(obj.attachments):
      return "Требуется прикрепить хотя бы 1 файл аудио формата", [], 1

    for a in obj.attachments:
      tofile = io.BytesIO()
      form = a.filename.split('.')[-1]

      try:
        audio = aus.from_file(io.BytesIO(await a.read()), format=form)
      except pydub.exceptions.CouldntDecodeError:
        text = f'Файлы формата {form} не поддерживается'

      audio.export(tofile, format='wav')
      recognizer = sr.Recognizer()

      chunk_duration = 90 * 1_000
      chunks = math.ceil(len(audio) / chunk_duration)

      i = obj.attachments.index(a) + 1
      text += f"Файл {i}.{' ' if i in range(0,10) else ''} "

      for i in range(chunks):
        chunk = audio[i * chunk_duration:(i + 1) * chunk_duration]
        with io.BytesIO() as chunk_buffer:
          chunk.export(chunk_buffer, format='wav')
          chunk_buffer.seek(0)

          with sr.AudioFile(chunk_buffer) as source:
            recognizer.adjust_for_ambient_noise(source)
            chunk_audio = recognizer.record(source)

          try:
            res = recognizer.recognize_google(chunk_audio, language=lang)
            text += f"{res} "
          except sr.UnknownValueError:
            text += "... "
          except sr.RequestError:
            text += "(Ошибка запроса к API)"
          type = 0

  else:
    text = "Требуется дописать код языка, с использованием которого будет распознавание"
    type = 1

  return text, [], type
