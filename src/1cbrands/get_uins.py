import json
import os
import xml.etree.ElementTree as ET
from datetime import date
from suds.client import Client

import db


def get_uins_from_1cbrands(url):
    """
    Robot отправляет запрос в 1C Brands. 1C Brands передает API - список БИНов по дебиторской задолженности на дату.
    Для 1C Brands «Дата» будет входным параметром, выходной параметр будет «список БИНов».
    Robot фиксирует дату списка БИНов, полученных c 1C Brands. Например, если была выгрузка массива
    контрагентов 1 декабря, то должна стоять пометка, что эти контрагенты были выгружены 1 декабря
    """
    today = date.today()
    # Robot отправляет запрос в 1C Brands
    try:
        client = Client(url)
        result = client.service.Adata(today.strftime("%Y%m%d"))
    except Exception as e:
        print(f"Ошибка post запроса в {url}: {e}")
        raise SystemExit(e)
    print("Robot отправляет запрос в 1C Brands.")
    print()

    # 1C Brands передает API - список БИНов по дебиторской задолженности на дату.
    root = ET.fromstring(result)
    all_new_uins = {child[0].text: child[1].text for child in root[2:] if child[0].text}

    print("1C Brands передает API - список БИНов по дебиторской задолженности на дату.")
    print()

    db.insert_data_one_c([(key, value, today.strftime("%Y-%m-%d")) for key, value in all_new_uins.items()])

    all_new_uins = list(all_new_uins.keys())
    # ДЛЯ ДЕМОНСТРАЦИЙ.
    # Сохраняем список Бинов полученных c 1C Brands без изменений в json файл имя которого сегодняшное дата
    data__ = {"date": today.strftime("%d.%m.%Y"),
              "uins": all_new_uins
              }

    if not os.path.exists(f"C:\\Users\\kasymzhan.asimov\\PycharmProjects\\1cbrands\\src\\uins_1C\\{today.strftime('%d.%m.%Y')}.json"):
        try:
            with open(f"C:\\Users\\kasymzhan.asimov\\PycharmProjects\\1cbrands\\src\\uins_1C\\{today.strftime('%d.%m.%Y')}.json", "w") as outfile:
                json.dump(data__, outfile)
        except Exception as e:
            print(f"Ошибка создание json файла {today.strftime('%d.%m.%Y')}.json: {e}")
            raise SystemExit(e)
    print("Сохраняем список Бинов полученных c 1C Brands без изменений в json файл имя которого сегодняшное дата")
    print()

    # Получаем бины которые были уже проверены
    try:
        with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\verified.json") as f:
            verify_data = json.load(f)
    except Exception as e:
        print(f"Ошибка открытие json файла verified.json: {e}")
        raise SystemExit(e)

    # удаляем бины которые уже были проверены в течений 20 дней
    for elem in all_new_uins:
        for key in verify_data:
            if elem in verify_data[key]:
                if elem in all_new_uins:
                    all_new_uins.remove(elem)

    # БИНы которые не были проверены за прeд 20 дней сохранены в json файл brands.json
    data__ = {"date": today.strftime("%d.%m.%Y"),
              "uins": all_new_uins
              }
    try:
        with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\brands.json", "w") as outfile:
            json.dump(data__, outfile)
    except Exception as e:
        print(f"Ошибка открытие json файла brands.json: {e}")
        raise SystemExit(e)
    print("БИНы которые не были проверены за прeд 20 дней сохранены в json файл brands.json.")
    print()

    print("Завершен процесс получение БИНов из 1C Brands и сохранение их в файлы.")
    print()
