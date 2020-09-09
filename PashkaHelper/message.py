from json import load


with open('text.json', 'r', encoding='UTF-8') as json_file:
    text = load(json_file)
