import json


def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def load_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            return data
    except:
        return []


if __name__ == '__main__':
    write_json('./data/tasks.json', [{'text': 'text', 'images': [], 'channels': []}])