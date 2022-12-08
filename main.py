from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = r'https://www.moex.com/'
timeout = 15

edge = webdriver.Edge()
edge.get(url)
assert 'Московская Биржа' in edge.title

try:
    element = edge.find_element(By.CLASS_NAME, 'header')
    waits = WebDriverWait(edge, timeout)\
        .until(EC.visibility_of(element))
    m_b = edge.find_element(By.XPATH, '//*[@onclick="showBurgerMenu()"]')
    ActionChains(edge).move_to_element(m_b).click(m_b)
    input()
finally:
    print('end')
    edge.quit()
