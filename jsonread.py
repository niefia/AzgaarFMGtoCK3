import json
import re

def remove_emoji(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def remove_emoji_from_json(json_file_path, output_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = remove_emoji(value)
    with open(output_file_path, 'w') as json_file:
        json.dump(data, json_file)

if __name__ == '__main__':
    json_file_path = 'emoji.json'
    output_file_path = 'noemoji.json'
    remove_emoji_from_json(json_file_path, output_file_path)
