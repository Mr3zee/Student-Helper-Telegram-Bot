import json

with open('text.json', 'r', encoding='UTF-8') as json_file:
    data = json.load(json_file)


def get_text(name, language_code):
    if language_code not in data:
        language_code = 'en'
    return data[language_code][name]


def make_list(films: dict, header, language_code):
    text = header
    for ticked in films['ticked']:
        text += '\n' + ticked + get_text('ticked_mark', language_code) + '\n'
    for unticked in films['unticked']:
        text += '\n' + unticked + get_text('unticked_mark', language_code) + '\n'
    return text
