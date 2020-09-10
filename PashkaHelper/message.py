from json import load
from PashkaHelper.config import text_file_path

with open(text_file_path, 'r', encoding='UTF-8') as json_file:
    text = load(json_file)
