from json import load
from PashkaHelper.config import text_file_path

with open(text_file_path, 'r', encoding='UTF-8') as json_file:
    data = load(json_file)


def get_text(name, language_code):
    if language_code not in data:
        language_code = 'ru'
    return data[language_code][name]
