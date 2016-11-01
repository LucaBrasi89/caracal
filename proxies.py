#! /usr/bin/python3

#        отступы пробелами
#        by Andrew Sotnikov aka Luca Brasi,
#        e-mail: andruha.sota@mail.ru
#        --------------
#         Получает прокси со сторонних сайтов. Добавляет их MySQL базу, после,
#         занимаеться поддержанием базы в актуальном состоянии.
#         Для работы нужно создать MySQL db 'proxy'



from lxml import html
import requests, time, saulog, os
from saumysql import Crud
from subprocess import call, PIPE




# Если по каким то причинам таблицы proxies нету, то она создается.

class Preparing:

    def __init__(self):

        crud=Crud('localhost','andrew','andrew','proxy')
        #Проверить наличие прокси
        self.checkProxiesTable()

    def __del__(self):

        self.crud.closeConnection()

    #Проверяет наличие таблицы proxies. Если ее нет, то создает.
    #В противном случае проходит мимо
    def checkProxiesTable(self):

        self.crud=Crud('localhost','andrew','andrew','proxy')
        self.crud.sql='SHOW TABLE STATUS LIKE \'proxies\''
        result=self.crud.readAct()

        # Таблицы нету, её прийдеться создать
        if  len(result) == 0:
            print('Нету таблицы с прокси адресами! Щас создадим')
            #Cоздадим таблицу proxies
            self.crud.sql='''CREATE TABLE proxies (
                             id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
                             ip_address VARCHAR(20),
                             port SMALLINT, 
                             time INT, 
                             UNIQUE (ip_address));'''
            result=self.crud.createAct()


        #В противном случае можно завязывать с этапом создания proxies
        else :
            print('proxies?! Походу есть такая таблица!')



# Механизм захвата прокси. Осуществляеться переход по заданному URL и дальнейший
# парсинг страницы.
class GetProxy:

    logfile='/var/log/andrew/proxies.log'
    
    def __init__(self):


        URL='http://hideme.ru/proxy-list/?country=CNCZFRDEINNOPLRUSIESSETRUAGB&type=h#list'
        headers = {
           'User-Agent': 'Lynx/2.8.8pre.4 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.12.23' }    
#        page = requests.get('http://hideme.ru/proxy-list/?country=RUGBUS#list', headers=headers)
        page = requests.get(URL, headers=headers)
        tree = html.fromstring(page.text)


        ip_addresses = tree.xpath("//*[@id='content-section']/section[1]/div/table/tbody/tr/td[1]")
        ports = tree.xpath("//*[@id='content-section']/section[1]/div/table/tbody/tr/td[2]")

        for ip_address, port in zip(ip_addresses,ports):
            
            ip_address = ip_address.text
            port = port.text
            print('ip_address: {0:20}; port: {1}'.format(ip_address, port))
            proxyObj = ProxyAct(ip_address,port)
            proxyObj.addProxy()
            
        saulog.WriteLog(self.logfile, '{0:*^90}'.format(' КОНЕЦ ПРОЦЕДУРЫ '))




# Основные действия рабты с прокси
class ProxyAct:

    def __init__(self,ip_address,port):
    
        self.ip_address = ip_address
        self.port = port
        self.crud = Crud('localhost', 'andrew', 'andrew', 'proxy')

    # проверяет прокси на доступность. Если прокси не рабочий он игнорируеться.
    def checkProxy(self):
    
        timeout = 10
        result = call('curl -s --connect-timeout {0} -x {1}:{2} http://google.com'.format(
                        timeout, self.ip_address, self.port), stdout=PIPE , shell=True)

        if result == 0:
            print('Всё путем! IP: {0:16} - хороший'.format(self.ip_address))

            return True
        else:
            print('Плохо, не подошел')

            return False

    # добавляет прокси в БД
    def addProxy(self):
        
        if (self.checkProxy()) == True:

            self.crud.sql=('''INSERT INTO proxies (ip_address, port, time)
                             VALUES ('{0}', '{1}', '{2}')'''.format(self.ip_address,
                             self.port, round(time.time())))
            self.crud.createAct()


    # удатяет прокси из БД. Используеться в основном в случаях если ранее
    # добавленный прокси устарел.
    def deleteProxy(self):

        self.crud.sql = ('DELETE FROM proxies WHERE ip_address=\'{0}\''.format(
            self.ip_address
        ))
        self.crud.deleteAct()



    def __del__(self):

        self.crud.closeConnection()


# Обновляет список прокси.
class UpdateProxies():

    logfile='/var/log/andrew/proxies.log'

    def __init__(self):

        self.working_proxies=[]
        self.not_working_proxies = []
        # получаем список всех прокси
        self.crud = Crud('localhost', 'andrew', 'andrew', 'proxy')
        self.crud.sql = ('SELECT * FROM proxies')

        # Вывод строки следующего формата '1, '79.188.42.46', 8080, 1473365169'
        # ////                             id, ip_address,    port,  gmt_time
        proxies=self.crud.readAct()

        # проверим прокси на работоспособность. Попутно подведем статитику
        # какие рабочие а какие нет.
        for elem in proxies:

            proxy = ProxyAct(elem[1], elem[2])
            if (proxy.checkProxy() == True):

                elapsed_hours = round((time.time() - elem[3])/3600)
                print('ip {0:18} рабочий! Уже аж {1:3} часов \n'.format(elem[1],
                                                               elapsed_hours))
                self.working_proxies.append(elem[1])

            else:

                print('ip {0:18} не рабочий! \n'.format(elem[1]))
                self.not_working_proxies.append(elem[1])
                proxy.deleteProxy()


        print('Рабочих ip - {0}'.format(len(self.working_proxies)))
        print('Не рабочих ip - {0}'.format(len(self.not_working_proxies)))

        # проверим старый ли лог. Возьмем его размер


        cur_log_size = os.path.getsize(self.logfile)
        # лимит файл 10К
        logfile_size_limit = 10000
        if (cur_log_size) >= logfile_size_limit:

            os.remove(self.logfile)
            f=open(self.logfile, 'w')

            f.write('{0:#>100}\n{1:#^100}\n{2:#>100}'.format(
                '', ' This is log file with proxies ', '\n'*2))
            f.close()


        try:
        
            # Пишем инфу в лог
            # получим самый старый и самый молодой возраст прокси
            self.crud.sql = 'SELECT MIN(time), MAX(time) FROM proxies'
            res = self.crud.readAct()
            # Переведи мне все это в часы
            older_proxy = round((time.time() - res[0])/3600)
            younger_proxy = round((time.time() - res[1])/3600)

            # Запишем инфу в лог
            saulog.WriteLog(self.logfile, 'Рабочих ip - {0}'.format(
                len(self.working_proxies)))
            saulog.WriteLog(self.logfile, 'Не рабочих ip - {0}'.format(
                len(self.not_working_proxies)))
            saulog.WriteLog(self.logfile, 'Возраст самого старого прокси - {0} часов'.format(
            older_proxy))
            saulog.WriteLog(self.logfile, 'Возраст самого недавнего прокси - {0} часов\n\n'.format(
            younger_proxy))
            # Лог записали
        except TypeError:
            
            print('не получилось...')
            
        

        self.crud.closeConnection()

if __name__ == "__main__":

    #проверим не легла ли сеть
    ping = call('ping -c 4 google.com', shell=True)
    if ping == 0:

        Preparing()
        UpdateProxies()
        GetProxy()
        
    else:
        print('сеть легла. Не буду ничего делать...')

