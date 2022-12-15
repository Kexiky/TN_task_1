from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
from datetime import date
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

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
    except:
        print("Менню подтверждения отсутствует")
    try:
        data = edge.find_element(By.CLASS_NAME, 'tablels')
        WebDriverWait(edge, timeout) \
            .until(EC.visibility_of(data))
        text_t = data.text
        return text_t
    except:
        return []

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
    table['Значение курса промежуточного клиринга'] = table['Значение курса промежуточного клиринга'].replace('-', np.nan)
    table['Значение курса промежуточного клиринга'] = table['Значение курса промежуточного клиринга'].str.replace(',', '.').astype('float64')
    table['Значение курса основного клиринга'] = table['Значение курса основного клиринга'].replace('-', np.nan)
    table['Значение курса основного клиринга'] = table['Значение курса основного клиринга'].str.replace(',', '.').astype('float64')
    return table

def auto_width_form_col(excel_file, data, sheet_name, form_col):
    form = excel_file.book.add_format({'num_format': '$#,##0.00_);[Red]($#,##0.00)'})
    i = 0
    for col in data:
        width_col = max(data.iloc[:, i].astype(str).map(len).max(), len(col))
        if i in form_col:
            excel_file.sheets[sheet_name].set_column(i, i, width_col + 1, form)
        else:
            excel_file.sheets[sheet_name].set_column(i, i, width_col + 1)
        i += 1
    return excel_file

def text_row(row_count):
    if (5 <= row_count <= 20) or (5 <= row_count % 10 <= 9) or (row_count % 10 == 0):
        text = f'{row_count} строк'
    elif (2 <= row_count%10 <= 4):
        text = f'{row_count} строки'
    else:
        text = f'{row_count} строка'
    return text

def send_message(email, password, subject, to_email, text, file=None, server='127.0.0.1'):
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = COMMASPACE.join(to_email)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    for f in file or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)
    smtp_server = smtplib.SMTP_SSL(server)
    smtp_server.login(email, password)
    smtp_server.sendmail(email, to_email, msg.as_string())
    smtp_server.close()

if __name__ == "__main__":
    #Указание данных URL помогает избежать первых шагов алгоритма, сразу попадая на страницу с нужным курсом
    url_USD_RUB = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=USD_RUB'
    url_EUR_RUB = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=EUR_RUB'
    url_CAD_RUB = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=CAD_RUB'
    current_date = date.today().strftime('%m.%Y')
    timeout = 15
    sheetname = 'Sheet_1'

    #Считывание данных из браузера (Пункты 1-6)
    table_rez = []
    for url in [url_USD_RUB, url_EUR_RUB]:
        text = get_data_from_url(url)
        table = text_to_table(text, current_date)
        if ((len(table) == 0) and (url == url_USD_RUB)):
            text = get_data_from_url(url_CAD_RUB)
        table_rez.append(table)

    #Подсчет "Изменения" согласно пункту 7
    last_col = pd.DataFrame()
    last_col['Изменение'] = table_rez[1]['Значение курса основного клиринга']/table_rez[0]['Значение курса основного клиринга']
    table_rez.append(last_col)
    table_rez = pd.concat(table_rez, axis=1)

    #Запись в excel-файл с предварительным выравниваем и форматированием (Пункты 5, 8-9)
    excel_path = f"{date.today().strftime('%Y.%m.%d')}_report.xlsx"
    excel = pd.ExcelWriter(excel_path)
    table_rez.to_excel(excel, sheet_name=sheetname, index=False, na_rep="-")
    excel = auto_width_form_col(excel_file=excel, data=table_rez, sheet_name=sheetname, form_col=[1, 3, 5, 7, 8])
    excel.save()

    #Отправка письма с корректным склонением слова "строк" (Пункты 10-11)
    email = 'MelkorLudoed@yandex.ru'
    password = 'scyvtqysosrwnkkq'
    to_email = 'h.o.r.s.e.p.o.w.e.r771@gmail.com'
    text_email = text_row(table_rez.shape[0])
    subject = 'Test'
    server = 'smtp.yandex.com:465'
    send_message(email=email,
                 password=password,
                 subject=subject,
                 to_email=to_email,
                 text=text_email,
                 file=[excel_path],
                 server=server)