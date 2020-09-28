from json import load
from static.config import text_json_file_path, text_mlw_file_path
from util.mlw_tools import MLWText, mlw_load

with open(text_json_file_path, 'r', encoding='UTF-8') as json_file:
    with open(text_mlw_file_path, 'r', encoding='UTF-8') as mlw_file:
        mlw_text = mlw_load(mlw_file)
        json_text = load(json_file)

        data = {'ru': {}}
        for language, text in json_text.items():
            for key, value in text.items():
                data[language][key] = MLWText(key, [value])

        for key, value in mlw_text.items():
            data['ru'][key] = value


def get_text(name, language_code) -> MLWText:
    if language_code not in data:
        language_code = 'ru'
    return data[language_code][name]
