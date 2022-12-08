from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np

def text_to_table(text):
    table = text.split("\n")[2:]
    table = np.array([x.split() for x in table])
    table = pd.DataFrame({
        'Дата': table[:, 0],
        'Значение курса промежуточного клиринга': table[:, 1],
        'Время': table[:, 2],
        'Значение курса основного клиринга': table[:, 3],
        'Время': table[:, 4]
    })
    return table

url_USD_RUB = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=USD_RUB'
url_EUR_RUB = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=EUR_RUB'
timeout = 15


edge = webdriver.Edge()
edge.get(url_USD_RUB)
edge.fullscreen_window()

assert 'Московская Биржа' in edge.title

try:
    agree = edge.find_element(By.LINK_TEXT, 'Согласен')
    WebDriverWait(edge, timeout)\
        .until(EC.visibility_of(agree))
    agree.click()
    data = edge.find_element(By.CLASS_NAME, 'tablels')
    WebDriverWait(edge, timeout) \
        .until(EC.visibility_of(data))
    text_t = data.text
    table = text_to_table(text_t)
    print(table)
finally:
    edge.close()