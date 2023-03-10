from datetime import date

import pyodbc


# Connect to the database
def connect():
    # Connect to the database
    cnxn = pyodbc.connect("DRIVER={SQL Server};"
                          "SERVER=172.16.245.139,1433;"
                          "DATABASE=RG_BRANDS_ADATA;"
                          "UID=python1;"
                          "PWD=LqwE53P%")

    return cnxn


def select_all():
    # Query the database for all rows in the test table
    cnxn = connect()
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM testtable")

    # Fetch all the rows
    rows = cursor.fetchall()

    # Print the rows
    for row in rows:
        print(row)


def insert_data_adata(data):
    # Insert a new row with data into the test table
    cnxn = connect()
    cursor = cnxn.cursor()
    query = "INSERT INTO adata_data (БИН, Наименование, Руководитель, Регион, Адрес, Основной_ОКЭД, " \
            "Вид_деятельности, Вторичный_ОКЭД, Вид_деятельности_для_вторчиного_ОКЭД, Размер_предприятия," \
            "Плательщик_НДС, Налоги_за_последние_5_лет, Участие_в_госзакупках, " \
            "Участие_в_закупках_Самрук_Казына, В_списке_Бездействующее_предприятие, В_списке_Банкрот, " \
            "В_списке_Регистрация_признана_недействительной, " \
            "В_списке_Реорганизован_с_нарушением_норм_Налогового_кодекса," \
            "В_списке_Отсутствует_по_юридическому_адресу, В_списке_Лжепредприятие, " \
            "В_списке_налогоплательщиков_имеющих_налоговую_задолженность_более_150_МРП, " \
            "В_списке_налогоплательщиков_находящихся_на_стадии_ликвидации, Арест_на_банковские_счета, " \
            "Арест_на_имущество, Временное_ограничение_на_выезд_из_РК, Запрет_на_регистрационные_действия_ФЛ, " \
            "Запрет_на_регистрационные_действия_ЮЛ, Запрет_на_совершение_нотариальных_действий, " \
            "Должник_по_исполнительным_производствам, " \
            "Должник_временно_ограниченный_на_выезд_из_Республики_Казахстан, " \
            "Задолженность_по_налогам_и_таможенным_платежам, Участие_в_судебных_делах, Бывшие_наименования, " \
            "Бывшие_адреса, Бывшие_руководители, Бывшие_учредители, Благонадежность, Cтепень_риска, " \
            "ДАТА_ФОРМИРОВАНИЕ, ДАТА_ВЫГРУЗКИ_1С) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?," \
            "?,?,?,?,?,?,?,?,?,?)"

    cursor.executemany(query, data)
    cnxn.commit()
    print('All uins from adata have been successfully added to the database')


def insert_data_one_c(data):
    # Insert a new row with data into the test table
    cnxn = connect()
    cursor = cnxn.cursor()
    cursor.executemany("INSERT INTO one_c_data (БИН, СУММА_САЛЬДО, ДАТА_ФОРМИРОВАНИЕ) VALUES (?,?,?)", data)
    cnxn.commit()
    print('All new uins from 1C have been successfully added to the database')



