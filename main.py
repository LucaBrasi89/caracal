#! /usr/bin/python3

#        отступы пробелами
#        by Andrew Sotnikov aka Luca Brasi,
#        e-mail: andruha.sota@mail.ru
#        --------------

import random, requests, time, os, argparse, re, sys
from saumysql import Crud
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import *

class Program_input:

    def __init__(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('--site', help='name of site for promoting. Simply, '
                                           'without filename extension. For instance, '
                                           ' write \'example\' instead of \'example.txt\'.')
        args = parser.parse_args()

        self.filename_noext = str(args.site) #Имя файла без расширения

        self.parseConfig()
        self.getURL()
        self.getKeywords()
        self.getUser_agents()



    def parseConfig(self):

        self.backToRootDir()

        config_file = self.filename_noext + '.cfg'  # Добавим расширение
        os.chdir('sites_for_promote')

        f = open(config_file)

        # пройдемся по файлу конфига и распарсим переменные
        for line in f:

            if (re.search(r'(?<=domain_name=).+?(?=$)', line)) != None:
                self.domain_name = re.search(r'(?<=domain_name=).+?(?=$)',line).group()

            elif (re.search(r'(?<=rqst_quantity=).+?(?=$)', line)) != None:
                self.rqst_quantity = re.search(r'(?<=rqst_quantity=).+?(?=$)',line).group()
                self.rqst_quantity = int(self.rqst_quantity)

            elif (re.search(r'(?<=perct_of_drefer=).+?(?=$)', line)) != None:
                self.perct_of_drefer = re.search(r'(?<=perct_of_drefer=).+?(?=$)',line).group()

            elif (re.search(r'(?<=aver_page_tm=).+?(?=$)', line)) != None:
                self.aver_page_tm = re.search(r'(?<=aver_page_tm=).+?(?=$)',line).group()

            elif (re.search(r'(?<=deep_in_site=).+?(?=$)', line)) != None:
                self.deep_in_site = re.search(r'(?<=deep_in_site=).+?(?=$)',line).group()

            elif (re.search(r'(?<=update_links=).+?(?=$)', line)) != None:
                self.update_links = re.search(r'(?<=update_links=).+?(?=$)',line).group()

                # Если есть необходимость получить свежие ссылки, то будь добр, сделай
                # для меня это...
                if (int(self.update_links) == 1):
                    self.updateLinks(self.filename_noext)

            elif (re.search(r'(?<=threads=).+?(?=$)', line)) != None:
                self.threads = re.search(r'(?<=threads=).+?(?=$)',line).group()

            elif (re.search(r'(?<=interval_low_lim=).+?(?=$)', line)) != None:
                self.interval_low_lim = re.search(r'(?<=interval_low_lim=).+?(?=$)',line).group()
                self.interval_low_lim = int(self.interval_low_lim)

            elif (re.search(r'(?<=interval_upper_lim=).+?(?=$)', line)) != None:
                self.interval_upper_lim = re.search(r'(?<=interval_upper_lim=).+?(?=$)',line).group()
                self.interval_upper_lim = int(self.interval_upper_lim)


        f.close()


    def updateLinks(self):

        # запусти мне selenium. Отыщи все ссылки на странице. Вытащи оттуда href.
        # Удали повторяющие ссылки из списка и запиши их в файл.

        chromedriver = "/home/andrew/Загрузки/chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        driver.get('http://progreso.com.ua/')
        urls_raw=driver.find_elements_by_tag_name('a')
        urls = []
        for url in urls_raw:
            urls.append(url.get_attribute('href'))

        urls=set(urls)

        driver.quit()

        # откроем файл на запись
        links = open('../url_db/{0}.url'.format(self.filename_noext), 'w')
        i=0
        for line in urls:
            if (line.count('?') != 0):
                links.write(line+'\n')
                i=i+1
        links.close()
        print('Было записано {0:4} ссылок'.format(i))

    # парсим URL из файла конфига. Добавляем им в self.URL_for_walk
    def getURL(self):

        links = open('../url_db/{0}.url'.format(self.filename_noext))
        self.URL_for_walk = []
        for line in links:
            self.URL_for_walk.append(line)


        links.close()

    # парсим keywords из файла конфига. Добавляем им в self.keywords
    def getKeywords(self):

        self.backToRootDir()
        os.chdir('sites_for_promote')

        self.keywords = []
        f = open(self.filename_noext+'.cfg')
        # флаг начала записи в keywords
        start=False
        for line in f:


            # если начался keyword - пиши-ка сразу в список
            if start == True:
                self.keywords.append(line.strip())

            # если встретился keyword поменяй флаг
            if line.count('<keywords>') != 0:

                start = True
             # закрывающий keyword? Выходи...
            elif line.count('</keywords>') != 0:
                break

        f.close()

        # мы случайно записали закрывающий тег. Удалим его потихому
        self.keywords.pop()


    # парсим user_agents из файла конфига. Добавляем им в self.user_agents
    def getUser_agents(self):

        self.backToRootDir()
        os.chdir('sites_for_promote')

        self.user_agents = []
        f = open(self.filename_noext + '.cfg')
        # флаг начала записи в user_agents
        start = False
        for line in f:

            # если начался keyword - пиши-ка сразу в список
            if start == True:
                self.user_agents.append(line.strip())

            # если встретился keyword поменяй флаг
            if line.count('<user_agents>') != 0:

                start = True
                # закрывающий keyword? Выходи...
            elif line.count('</user_agents>') != 0:
                break

        f.close()

        # мы случайно записали закрывающий тег. Удалим его потихому
        self.user_agents.pop()



    def backToRootDir(self):

        root_dir = (str(sys.argv[0]).split(os.path.basename(sys.argv[0])))[0]
        os.chdir(root_dir)



class GenParam(Program_input):


    def __init__(self,launch_way):

        Program_input.__init__(self)

        # получим интервал
        self.interval = random.randint(self.interval_low_lim, self.interval_upper_lim)

        # оформим user-agent
        self.user_agent = random.choice(self.user_agents)


        # получим URL к котрому будем обращаться
        self.url = random.choice(self.URL_for_walk)

        # получаем прокси
        self.crud = Crud('localhost', 'andrew', 'andrew', 'proxy')
        self.crud.sql = ('SELECT ip_address, port FROM proxies ORDER BY RAND() LIMIT 1')
        result = self.crud.readAct()
        self.proxy = '{0}:{1}'.format(result[0], result[1])


        launch_ways=range(0,2)

        launch_way = random.choice(launch_ways)

        # определяем по какому пути идти
        if launch_way == 0:
            self.googleSearch()

        elif launch_way ==1:
            self.directWalk()

    def googleSearch(self):

        # делаем запрос к серверу

        print('Это метод googleSearch')
        try:
            chromedriver = "/home/andrew/Загрузки/chromedriver"
            os.environ["webdriver.chrome.driver"] = chromedriver

            # получим keywords
            keyword = random.choice(self.keywords)

            # заменим user_agent'a
            chrome_options = webdriver.ChromeOptions()

            chrome_options.add_argument(
                "--user-agent={0}".format(self.user_agent))

            driver = webdriver.Chrome(chromedriver,
                                      chrome_options=chrome_options)

            driver.get("http://google.com")

            time.sleep(random.randint(1, 5))

            search = driver.find_element_by_name('q')
            search.send_keys("{0} site:progreso.com.ua".format(keyword))
            search.send_keys(
                Keys.RETURN)  # hit return after you enter search text
            time.sleep(random.randint(4,12))  # sleep for 5 seconds so you can see the results

            elem = driver.find_element_by_xpath('''.//*[@id='rso']/div/div[1]/div/h3/a ''')
            elem.click()
            time.sleep(random.randint(20, 31))

            print('{0}\n{1}\n{2}\n____'.format(self.url, self.proxy,
                                               self.user_agent))



        except Exception:

            print('FUCK!')

        finally:
            driver.quit()


    def directWalk(self):

        # делаем запрос к серверу
        
        print('Это метод directWalk')

        try:
            chromedriver = "/home/andrew/Загрузки/chromedriver"
            os.environ["webdriver.chrome.driver"] = chromedriver

            # заменим user_agent'a


            # используем прокси
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--proxy-server={0}'.format(self.proxy))

            chrome_options.add_argument("--user-agent={0}".format(self.user_agent))

            driver = webdriver.Chrome(chromedriver,chrome_options=chrome_options)
#            driver.get("http://www.whoishostingthis.com/tools/user-agent/")

            time.sleep(random.randint(5,20))
            driver.get(self.url)
            driver.find_element_by_tag_name('body').send_keys(
                Keys.CONTROL + 't')
            driver.find_element_by_tag_name('body').send_keys(
                Keys.CONTROL + 'w')
            time.sleep(random.randint(5,20))

            print('{0}\n{1}\n{2}\n____'.format(self.url, self.proxy, self.user_agent))



        except Exception:

            print('FUCK!')

        finally:
            driver.quit()





class Executor(Program_input):

    def __init__(self):

        Program_input.__init__(self)


        prev_iter=time.time()

        for request in range(self.rqst_quantity):
            print('попытка № {0}'.format(request))
            genObj = GenParam(0)
            print('Ждем-с {0} секунд'.format(genObj.interval))
            cur_iter = time.time()
            elapsed = round(cur_iter - prev_iter)
            print('прошло времени {0:5} секунд'.format(elapsed))
            prev_iter = time.time()
            time.sleep(genObj.interval)




if __name__ == "__main__":


    Executor()
