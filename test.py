from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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
        return text_t
    except:
        return []


timeout = 15
url = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=USD_RUB'
edge = webdriver.Edge()
edge.get(url)
text = get_data_from_url(url)
print(text)


