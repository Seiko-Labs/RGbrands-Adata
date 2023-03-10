import os
import time
import config
import requests


def file_location(_token):
    """
    Периодично Robot должна отправлять запрос о готовности данных в Adata.
    В случае получения ответа «wait» запрос о готовности необходимо провести позднее.
    В случае готовности данных приходит ссылка на скачивание  файла формата Excel c
    данными и список БИНов не прошедших проверку
    """
    try:
        file_response = requests.get(
            f'https://api.adata.kz/api/mass-info/check/{config.TOKEN_AUTH}?token={_token}'
        )
    except requests.exceptions.RequestException as e:
        print(f"Ошибка get запроса в https://api.adata.kz/api/mass-info/check/{config.TOKEN_AUTH}?token={_token}: {e}")
        raise SystemExit(e)

    file_json = file_response.json()
    print(file_json)
    if file_json["message"] == 'ready':
        return file_json["data"]["file_location"]
    else:
        # Excel файл еще не готов. Повторный запрос через 60 секунд
        print("Excel файл еще не готов. Повторный запрос через 60 секунд")
        print()
        time.sleep(60)
        return file_location(_token)


def download_file(token_id):
    """
    01.5 Сохранение данных
    При получении ссылки на скачивание файла формата Excel c данными, данный список необходимо сохранить в
    сетевую папку \\172.16.245.8\QlikView\XLS\Reliability
    """
    _url = file_location(token_id)
    print(r"Сохраняем Excel файл в директорий C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\adata_response")
    print()
    local_filename = _url.split('/')[-1]
    with requests.get(_url, stream=True) as r:
        r.raise_for_status()
        os.chdir(r'C:\Users\kasymzhan.asimov\PycharmProjects\1cbrands\src\adata_response')
        # Сохраняем Excel файл в директорий \\172.16.245.8\QlikView\XLS\Reliability
        with open(local_filename, 'wb') as file:
            for chunk in r.iter_content(chunk_size=8192):
                file.write(chunk)
    return local_filename
