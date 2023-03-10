import datetime
import json


def write_to_verify_json(new_data: list):
    today = datetime.date.today()

    try:
        with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\verified.json", 'r') as jsonfile:
            verified = json.load(jsonfile)
    except Exception as e:
        print(f"Ошибка открытие json файла verified.json: {e}")
        raise SystemExit(e)

    entry = {today.strftime("%d.%m.%Y"): new_data}

    for k, v in entry.items():
        if k in verified:
            verified[k].extend(v)
        else:
            verified[k] = v

    new_dict = {}

    for _elem in verified:
        day_of_uins = datetime.datetime.strptime(_elem, '%d.%m.%Y')
        delta = datetime.datetime.now() - day_of_uins
        if delta.days < 20:
            new_dict[_elem] = verified[_elem]
    try:
        with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\verified.json", 'w') as jsonfile:
            json.dump(new_dict, jsonfile)
    except Exception as e:
        print(f"Ошибка добавление бинов в json файла verified.json: {e}")
        raise SystemExit(e)
