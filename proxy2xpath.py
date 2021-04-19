
import os
import threading
import time
from random import randint

import requests
from lxml import html


class Proxy:
    """Класс объекта "Список прокси"

    Пример:
    pr_obj = Proxy()
    print(pr_obj.get_proxy_list)
    print(pr_obj.get_rnd_proxy)
    """

    def __init__(self):
        self.true_proxy = []
        # устанавливаем каталог программы
        dir_prog = os.path.dirname(os.path.abspath(__file__))
        os.chdir(dir_prog)
        # 1. если файл > 4 часов, обновляем его
        if os.path.exists(dir_prog + '\sp_prox.txt'):
            file_time = os.path.getmtime(dir_prog + '\sp_prox.txt')  # дата создания файла
            curr_tm_sec = time.time()
            delta_time = curr_tm_sec - file_time
            if delta_time // (3600 * 4) > 0:
                self._cr_list_proxy()
        # 2. проверяем наличие фала sp_prox.txt, при его отсутствуии, создаём
        if not os.path.exists(dir_prog + '\sp_prox.txt'):
            self._cr_list_proxy()
        with open('sp_prox.txt', 'r') as fl:
            self._proxy_list = [s.strip() for s in fl]

    def _cr_list_proxy(self):
        print('Start create proxy list')
        ls = self.GetProxy()
        self._start_thr(ls_proxy=ls)
        if len(self.true_proxy) > 0:
            with open('sp_prox.txt', 'w') as fl:
                for s in self.true_proxy:
                    fl.write(s + '\n')
        print('Proxy list created')

    def GetProxy(self):
        """Список прокси

        :return: Список прокси вида ['125.155.55.8:8080']
        """
        headers = {
            'Host': 'www.ip-adress.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        res = requests.get('https://www.ip-adress.com/proxy-list', headers=headers)
        HtmlTree = html.fromstring(res.content)
        ls_ip = HtmlTree.xpath("//table/tbody/tr/td")
        ls = [el for el in ls_ip if len(el)]
        ls_res = []
        for el in ls:
            if len(list(el.xpath("./text()"))) > 0:
                ip = el.xpath("./a/text()")
                port = list(el.xpath("./text()"))
                ls_res.append(ip[0] + port[0])
        return ls_res

    def ChProxy(self, proxy):
        """Проверка прокси на работоспособность

        :param proxy: прокси вида '125.155.55.8:8080'
        :return: True / False
        """
        try:
            r = requests.get('https://www.myip.com/', proxies={'https': proxy})  # !!! {'https': prox})
            HtmlTree = html.fromstring(r.content)
            my_ip = HtmlTree.xpath("//*[@id='ip']/text()")[0]
            ch_ip = True if my_ip == proxy.split(':')[0] else False
        except:
            ch_ip = False
        if ch_ip:
            self.true_proxy.append(proxy)
        return ch_ip

    def _start_thr(self, ls_proxy):
        """Запуск потоков проверки прокси

        :param ls_proxy: Список прокси
        :return:
        """
        ls_thread = []
        for proxy in ls_proxy:
            thread = threading.Thread(target=self.ChProxy, args=(proxy,))
            ls_thread.append(thread)
            thread.start()
        for thread in ls_thread:
            thread.join()

    @property
    def get_proxy_list(self):
        """ Возвращает список прокси

        :return: Список прокси
        """
        ls = self._proxy_list
        return ls

    @property
    def get_rnd_proxy(self):
        """Возвращает случайный адрес прокси из списка

        :return: '125.155.55.8:8080'
        """
        #
        rnd_proxy = self._proxy_list[randint(0, len(self._proxy_list) - 1)]
        return rnd_proxy


if __name__ == '__main__':
    pr = Proxy()
    print(pr.get_proxy_list)
    print(pr.get_rnd_proxy)
