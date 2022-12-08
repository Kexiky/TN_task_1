from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
from datetime import date
import openpyxl

def get_data_from_url(url):
    edge = webdriver.Edge()
    edge.get(url)
    edge.fullscreen_window()

    assert 'Московская Биржа' in edge.title

    try:
        agree = edge.find_element(By.LINK_TEXT, 'Согласен')
        WebDriverWait(edge, timeout) \
            .until(EC.visibility_of(agree))
        agree.click()
        data = edge.find_element(By.CLASS_NAME, 'tablels')
        WebDriverWait(edge, timeout) \
            .until(EC.visibility_of(data))
        text_t = data.text

    finally:
        edge.close()
        return text_t

def text_to_table(text, c_d):
    table = text.split("\n")[2:]

    table = np.array([x.split() for x in table])
    table = pd.DataFrame({
        'Дата': table[:, 0],
        'Значение курса промежуточного клиринга': table[:, 1],
        'Время': table[:, 2],
        'Значение курса основного клиринга': table[:, 3],
        'Время': table[:, 4]
    })
    table = table[(table['Дата'].str[3:5] == c_d[:2]) & (table['Дата'].str[6:] == c_d[3:])]
    if len(table) == 0:
        return []
    table['Значение курса промежуточного клиринга'] = table['Значение курса промежуточного клиринга'].str.replace(',', '.').astype('float64')
    table['Значение курса основного клиринга'] = table['Значение курса основного клиринга'].str.replace(',', '.').astype('float64')
    return table


url_USD_RUB = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=USD_RUB'
url_EUR_RUB = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=EUR_RUB'
url_CAD_RUB = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=CAD_RUB'

current_date = date.today().strftime('%m.%Y')
timeout = 15

table_rez = []
for url in [url_USD_RUB, url_EUR_RUB]:
    text = get_data_from_url(url)
    table = text_to_table(text, current_date)
    if ((len(table) == 0) and (url == url_USD_RUB)):
        text = get_data_from_url(url_CAD_RUB)
    table_rez.append(table)

last_col = table_rez[1]['Значение курса основного клиринга']/table_rez[0]['Значение курса основного клиринга']
for i in table_rez:
    print(i)
print(last_col)

