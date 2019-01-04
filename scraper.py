import csv
import requests
import datetime
import time
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool


def write_to_file(data, method, delimiter):
    """Function for writing parsed data to csv-file"""
    output_file = 'data.csv'
    with open(output_file, method, newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=delimiter)
        writer.writerows([data])


def get_page(date):
    """Function takes date as an argument.
        Send cookies to the url.
        Get response as html page.
        Call function 'get_data_from_table' for parsing with parameter - html page.
        Error handling and return message.
        Data types:
            date - str,
            page - Response"""
    session = requests.Session()
    try:
        data = {"FLG_Autoconsulta": 1}
        url = 'https://laboral.pjud.cl'
        session.post(url + '/SITLAPORWEB/InicioAplicacionPortal.do', data=data)
        session.get(url + '/SITLAPORWEB/AtPublicoViewAccion.do?tipoMenuATP=1')
        form_data = {'TIP_Consulta': 5,
                     'TIP_Lengueta': 'tdDos',
                     'SeleccionL': 0,
                     'ERA_Causa': 0,
                     'RUC_Tribunal': 4,
                     'FEC_Desde': date,
                     'FEC_Hasta': date,
                     'SEL_Trabajadores': 0,
                     'irAccionAtPublico': 'Consulta',
                     'COD_Tribunal': 0}
        page = session.post(url + '/SITLAPORWEB/AtPublicoDAction.do', data=form_data)
        get_data_from_table(page)
    except ConnectionError:
        print("Connection error")
        return None


def get_data_from_table(page):
    """Function for getting parsed data.
        Find table with data in html page, which is the argument.
        Scrape necessary information,
        call function for writing information to file.
        Data types:
            page - Response"""
    soup = BeautifulSoup(page.text, 'lxml')
    table = soup.find('table', id='filaSel')
    for row in table.find_all('tr'):
        data_list = []
        for column in row.find_all('td'):
            data_list.append(column.get_text().strip())
        write_to_file(data_list, 'a', '\t')


def generate_date(date):
    """Function get date as an argument.
        Generate date of each day from a given date to today.
        Return date.
        Data types:
            date - str,
            date_of_day - str"""
    date_list = date.split('/')
    date = datetime.datetime(int(date_list[2]), int(date_list[1]), int(date_list[0]))
    now = datetime.datetime.now()
    general_delta = abs(now - date)
    for delta in range(general_delta.days + 1):
        date_of_day = (date + datetime.timedelta(delta)).strftime('%d/%m/%Y')
        yield date_of_day


def main():
    start = time.time()
    write_to_file(['RIT', 'RUC', 'F. Ingreso', 'Caratulado', 'Tribunal'], 'w', '\t')
    date = '01/07/2018'
    pool = ThreadPool(20)
    pool.map(get_page, generate_date(date))
    print('Time of working script:', time.time() - start, 'sec')


if __name__ == '__main__':
    main()
