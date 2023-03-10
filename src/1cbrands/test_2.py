import json
import os
import openpyxl
import requests
from datetime import date

import db
from add_checked import write_to_verify_json
from download_response import download_file
from get_uins import get_uins_from_1cbrands

# import agent_initializetion


def send_uins_to_adata(portion_):
    """
    Отправляем 200 бинов порционно на проверку на сервис в Adata.
    При отправке на сервис возвращается ID  запроса.
    """
    try:
        with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\brands.json") as f:
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
    excel_file_name = download_file(token_id)

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

    insert_data = []
    for row in sheet.iter_rows(min_row=5, values_only=True):
        row_data = ()
        for value in row:
            if value is not None:
                row_data += (str(value),)
        row_data += (today.strftime("%Y-%m-%d"),)
        insert_data.append(row_data)

    db.insert_data_adata(insert_data)

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
        with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\brands.json", "w") as jsonFile:
            json.dump(data_, jsonFile)
    except Exception as e:
        print(f"Ошибка изменение бинов в json файла brands.json: {e}")
        raise SystemExit(e)

    print("Успешное завершение итераций")
    print()


def main():
    # Открываем файл brands.json и создаем  переменную uins_1C
    try:
        with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\brands.json") as f:
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

                    get_uins_from_1cbrands(url)

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

        get_uins_from_1cbrands(url)
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
    if not os.path.exists(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\brands.json"):
        print("Создаем файл brands.json")
        try:
            with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\brands.json", 'w') as f_:
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
    if not os.path.exists(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\verified.json"):
        print("Создаем файл verified.json")
        print()
        try:
            with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\verified.json", 'w') as f_:
                data_ = {}
                json.dump(data_, f_)
        except Exception as e_:
            print(f"Ошибка создание json файла verified.json: {e_}")
            raise SystemExit(e_)
        else:
            print("Файл verified.json успешно создан")

    # Открываем файл brands.json и создаем  переменную uins_1C
    try:
        with open(r"C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\data\brands.json") as f_:
            data_ = json.load(f_)
    except Exception as e_:
        print(f"Ошибка открытие json файла brands.json: {e_}")
        raise SystemExit(e_)

    main()
