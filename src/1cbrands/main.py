import datetime
import json
import os
import time
from datetime import date

import openpyxl
import requests
from suds.client import Client
import xml.etree.ElementTree as ET
# import agent_initializetion


def write_to_verify_json(new_data: list):
    try:
        with open("../data/verified.json", 'r') as jsonfile:
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
        with open("../data/verified.json", 'w') as jsonfile:
            json.dump(new_dict, jsonfile)
    except Exception as e:
        print(f"Ошибка добавление бинов в json файла verified.json: {e}")
        raise SystemExit(e)


def file_location(_token):
    """
    Периодично Robot должна отправлять запрос о готовности данных в Adata.
    В случае получения ответа «wait» запрос о готовности необходимо провести позднее.
    В случае готовности данных приходит ссылка на скачивание  файла формата Excel c
    данными и список БИНов не прошедших проверку
    """
    try:
        file_response = requests.get(
            f'https://api.adata.kz/api/mass-info/check/{token_auth}?token={_token}'
        )
    except requests.exceptions.RequestException as e:
        print(f"Ошибка get запроса в https://api.adata.kz/api/mass-info/check/{token_auth}?token={_token}: {e}")
        raise SystemExit(e)

    file_json = file_response.json()
    print(file_json)
    if file_json["message"] == 'ready':
        return file_json["uins_1C"]["file_location"]
    else:
        # Excel файл еще не готов. Повторный запрос через 60 секунд
        print("Excel файл еще не готов. Повторный запрос через 60 секунд")
        print()
        time.sleep(60)
        return file_location(_token)


def download_file(_url: str):
    """
    01.5 Сохранение данных
    При получении ссылки на скачивание файла формата Excel c данными, данный список необходимо сохранить в
    сетевую папку \\172.16.245.8\QlikView\XLS\Reliability
    """
    print(r"Сохраняем Excel файл в директорий \\172.16.245.8\QlikView\XLS\Reliability")
    print()
    local_filename = _url.split('/')[-1]
    with requests.get(_url, stream=True) as r:
        r.raise_for_status()
        os.chdir(r'\\172.16.245.8\QlikView\XLS\Reliability')
        # Сохраняем Excel файл в директорий \\172.16.245.8\QlikView\XLS\Reliability
        with open(local_filename, 'wb') as file:
            for chunk in r.iter_content(chunk_size=8192):
                file.write(chunk)
    return local_filename


def get_uins_from_1cbrands():
    """
    Robot отправляет запрос в 1C Brands. 1C Brands передает API - список БИНов по дебиторской задолженности на дату.
    Для 1C Brands «Дата» будет входным параметром, выходной параметр будет «список БИНов».
    Robot фиксирует дату списка БИНов, полученных c 1C Brands. Например, если была выгрузка массива
    контрагентов 1 декабря, то должна стоять пометка, что эти контрагенты были выгружены 1 декабря
    """

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
    all_new_uins = [child[0].text for child in root[1:] if child[0].text]
    print("1C Brands передает API - список БИНов по дебиторской задолженности на дату.")
    print()

    # Сохраняем список Бинов полученных c 1C Brands без изменений в Ехсеl файл в сетевой папке
    os.chdir(r'\\172.16.245.8\QlikView\XLS\Reliability\Реестры БИНов с 1С')
    if not os.path.exists(f"БИН_1с_{today.strftime('%d_%m_%Y')}.xlsx"):
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "БИНы из 1С"
            ws.append((today.strftime("%d.%m.%Y"),))
            for item in all_new_uins:
                ws.append((item,))
            wb.save(f"БИН_1с_{today.strftime('%d_%m_%Y')}.xlsx")
            wb.close()
        except Exception as e:
            print(f"Ошибка создание Excel файла БИН_1с.xlsx: {e}")
            raise SystemExit(e)
    else:
        print(f"Excel файл БИН_1с_{today.strftime('%d_%m_%Y')}.xlsx уже существет---------------")
    print("Сохраняем список Бинов полученных c 1C Brands без изменений в Ехсеl файл в сетевой папке")
    print()

    os.chdir(cwd)

    # ДЛЯ ДЕМОНСТРАЦИЙ.
    # Сохраняем список Бинов полученных c 1C Brands без изменений в json файл имя которого сегодняшное дата
    data__ = {"date": today.strftime("%d.%m.%Y"),
              "uins": all_new_uins
              }

    if not os.path.exists(f"{today.strftime('%d.%m.%Y')}.json"):
        try:
            with open(f"{today.strftime('%d.%m.%Y')}.json", "w") as outfile:
                json.dump(data__, outfile)
        except Exception as e:
            print(f"Ошибка создание json файла {today.strftime('%d.%m.%Y')}.json: {e}")
            raise SystemExit(e)
    print("Сохраняем список Бинов полученных c 1C Brands без изменений в json файл имя которого сегодняшное дата")
    print()

    # Получаем бины которые были уже проверены
    try:
        with open("../data/verified.json") as f:
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
        with open("../data/brands.json", "w") as outfile:
            json.dump(data__, outfile)
    except Exception as e:
        print(f"Ошибка открытие json файла brands.json: {e}")
        raise SystemExit(e)
    print("БИНы которые не были проверены за прeд 20 дней сохранены в json файл brands.json.")
    print()

    print("Завершен процесс получение БИНов из 1C Brands и сохранение их в файлы.")
    print()


def send_uins_to_adata(portion_):
    """
    Отправляем 200 бинов порционно на проверку на сервис в Adata.
    При отправке на сервис возвращается ID  запроса.
    """
    try:
        with open("../data/brands.json") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка открытие json файла brands.json: {e}")
        raise SystemExit(e)

    # создаем переменную lst где храним бины ожидающих проверку
    lst_ = data["uins"]
    print(
        f"Извлекаем {len(lst_[:portion_])} БИН которые нужно проверить и передаем его в Адату")
    print()

    data_for_adata = lst_[:portion_]

    print(data_for_adata)
    print()

    dictionary = {
        "uins": data_for_adata
    }
    url_ = f'http://api.adata.kz/api/mass-info/company/{token_auth}'
    data_json = json.dumps(dictionary)
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url=url_, data=data_json, headers=headers)
        print(response.text)
        if response.status_code != 200:
            raise requests.ConnectionError
    except requests.exceptions.RequestException as e:
        print(f"Ошибка post запроса в {url_}: {e}")
        raise SystemExit(e)

    # Отправляем get запрос с token_id который мы получили когда отправили БИНы на проверку
    # Получаем excel файл с БИНами которые не прошли проверку
    print("Отправляем get запрос с token_id который мы получили когда отправили БИНы на проверку")
    print()

    token_id = str(response.json()["token"])
    print(token_id)
    print()
    excel_file_name = download_file(file_location(token_id))

    print("Получаем excel файл с БИНами которые не прошли проверку")
    print()
    print(excel_file_name)
    print()

    workbook = openpyxl.load_workbook(f'{excel_file_name}')
    os.chdir(cwd)
    try:
        sheet = workbook['Worksheet']
    except KeyError:
        sheet = workbook['Sheet1']
    not_checked_list = [str(elem.value) for elem in sheet['A'][4:] if elem.value is not None]

    print("БИНы которые не прошли проверку------------------------------------------------------------------------")
    print(list(set(not_checked_list)))
    print()

    print("БИНы которые прошли проверку")
    verified = set(data_for_adata) - set(not_checked_list)
    print(verified)
    print()

    # БИНы которые были проверены были сохранены в json файл verified.json где фиксируется дата
    print("БИНы которые были проверены были сохранены в json файл verified.json где фиксируется дата")
    write_to_verify_json(data_for_adata)
    print()

    # Удаляем из файла brands.json БИНы которые сегодня отправили на проверку
    print("Удаляем из файла brands.json БИНы которые сегодня отправили на проверку")
    print()
    for elem in data_for_adata:
        data_["uins"].remove(elem)

    try:
        with open("../data/brands.json", "w") as jsonFile:
            json.dump(data_, jsonFile)
    except Exception as e:
        print(f"Ошибка изменение бинов в json файла brands.json: {e}")
        raise SystemExit(e)

    print("Успешное завершение итераций")
    print()


def main():
    # Открываем файл brands.json и создаем  переменную uins_1C
    try:
        with open("../data/brands.json") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка открытие json файла brands.json: {e}")
        raise SystemExit(e)

    # создаем переменную lst где храним бины ожидающих проверку
    lst = data["uins"]

    # Если имеем БИНы которые нужно проверить
    if lst:
        print("Файл brands.json не пустой, направляем бины на проверку")
        print()

        if len(lst) < splits:
            print(f'Имеем {len(lst)} БИНов что меньше {splits} которые нужно направить на проверку')
            print()
            for _ in range(splits // portion):
                if len(lst) > portion:
                    print(f'направляем на проверку порционно по {portion}')
                    print()
                    send_uins_to_adata(portion)
                else:
                    print(f'направляем на проверку порционно по {len(lst)}')
                    print()
                    new_request_uins = portion - len(lst)
                    send_uins_to_adata(len(lst))

                    print(f"Поэтому отправяем новый запрос в 1с")
                    print()

                    get_uins_from_1cbrands()

                    send_uins_to_adata(new_request_uins)
            print("Успешное завершение процесса")

        else:
            print(f'Имеем {len(lst)} БИНов что больше {splits} которые нужно направить на проверку')
            print()
            print(f"Поэтому направляем на проверку порционно по {portion}")
            print()
            for _ in range(splits // portion):
                send_uins_to_adata(portion)
            print("Успешное завершение процесса")

    # Если brands.json пустой
    else:
        print("Файл brands.json пустой поэтому отправляем новый запрос в 1C Brands")
        print()

        get_uins_from_1cbrands()
        main()


if __name__ == '__main__':
    print("Запуск скрипта")
    print()
    # глобальные переменные
    url = "http://1ctestdbconsult/BrandsKZ82_Bagdat/ws/APIElma?wsdl"
    today = date.today()
    cwd = os.getcwd()
    splits = 100  # количество бинов отправляемых на проверку в день
    portion = 50  # количество бинов порционно отправляемых на проверку
    token_auth = 'iARqjDpJLuDSZZ5ajxQkCgR6gMx9aJqz'

    # Создаем файл brands.json если не существует
    if not os.path.exists("../data/brands.json"):
        print("Создаем файл brands.json")
        try:
            with open("../data/brands.json", 'w') as f_:
                data_ = {
                    "uins": []
                }
                json.dump(data_, f_)
        except Exception as e_:
            print(f"Ошибка создание json файла brands.json: {e_}")
            raise SystemExit(e_)
        else:
            print("Файл brands.json успешно создан")

    # Создаем файл verified.json если не существует
    if not os.path.exists("../data/verified.json"):
        print("Создаем файл verified.json")
        print()
        try:
            with open("../data/verified.json", 'w') as f_:
                data_ = {}
                json.dump(data_, f_)
        except Exception as e_:
            print(f"Ошибка создание json файла verified.json: {e_}")
            raise SystemExit(e_)
        else:
            print("Файл verified.json успешно создан")

    # Открываем файл brands.json и создаем  переменную uins_1C
    try:
        with open("../data/brands.json") as f_:
            data_ = json.load(f_)
    except Exception as e_:
        print(f"Ошибка открытие json файла brands.json: {e_}")
        raise SystemExit(e_)

    main()
