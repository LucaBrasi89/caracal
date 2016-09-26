#! /usr/bin/python3

#        отступы пробелами
#        by Andrew Sotnikov aka Luca Brasi,
#        e-mail: andruha.sota@mail.ru
#        --------------

import random, requests, time
from saumysql import Crud

class Program_input:

    request_quantity = 20 #Количество запросов к сайту
    percent_of_direct_refer = 100 #Доля прямых переходов
    URL_for_walk = ['http://progreso.com.ua/?p=1507',
                    'http://progreso.com.ua/?p=1494',
                    'http://progreso.com.ua/?p=1479',
                    'http://progreso.com.ua/?p=1468',
                    'http://progreso.com.ua/?p=1458',
                    'http://progreso.com.ua/?p=1449',
                    'http://progreso.com.ua/?p=1441',
                    'http://progreso.com.ua/?p=1434',
                    'http://progreso.com.ua/?p=1425',
                    'http://progreso.com.ua/?p=1412',
    ] #URL для прямых переходов
    keywords = [] #ключевые слова

    # диапазон интервалов для обращения к сайтам
    interval_low_limit = 300 #минимальный предел
    interval_upper_limit = 600  #максимальный предел

    # user_agent_fields
    user_agent=['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
                'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
                'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
                'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
                'Opera/12.0(Windows NT 5.2;U;en)Presto/22.9.168 Version/12.00',
                'Opera/12.0(Windows NT 5.2;U;en)Presto/22.9.168 Version/12.00',
                'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13; ) Gecko/20101203'
    ]


class GenParam(Program_input):


    def __init__(self):

        # получим интервал
        self.interval = random.randint(self.interval_low_limit, self.interval_upper_limit)

        # оформим user-agent
        user_agent = random.choice(self.user_agent)
        headers = {'User-Agent': user_agent}

        # получим URL к котрому будем обращаться
        url = random.choice(self.URL_for_walk)

        # получаем прокси
        self.crud = Crud('localhost', 'andrew', 'andrew', 'proxy')
        self.crud.sql = ('SELECT ip_address, port FROM proxies ORDER BY RAND() LIMIT 1')
        result = self.crud.readAct()
        self.proxy = 'http://{0}:{1}'.format(result[0], result[1])
        proxies = {'http': self.proxy}

        # делаем запрос к серверу
        try:
            requests.get(url, proxies=proxies, headers=headers)
            print('{0}\n{1}\n{2}\n_____'.format(url,proxies,headers))
        except Exception:
            print('FUCK!')


class Executor(Program_input):

    def __init__(self):

        for request in range(self.request_quantity):
            print('попытка № {0}'.format(request))
            genObj = GenParam()
            print('Ждем-с {0} секунд'.format(genObj.interval))
            time.sleep(genObj.interval)

if __name__ == "__main__":

    Executor()