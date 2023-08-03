import time
import datetime
import requests
from bs4 import BeautifulSoup

from django.db.utils import IntegrityError
from django.db.models import Q

from pubmed.models import Proxy


class ProxyParser:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'}

    def parse(self, *agrs, **kwargs):
        self.freeproxylist_ru()
        # self.checkerproxy_net()
        # self.freeproxylist_net()
        # self.hidemy_name()
        # self.advanced_name_ru()
        # self.free_proxy_cz()

    def hidemy_name(self, *agrs, **kwargs):
        source = 'hidemy.name'
        url = 'https://hidemy.name/ru/proxy-list/?type=s#list'
        response = requests.get(url, headers=self.headers, timeout=3)
        print(response, response.content)
        _html = BeautifulSoup(response.content, 'html.parser')
        proxy_list = []
        for tr in _html.select('table.table_block tbody tr'):
            print(tr)
            item = dict(
                source=source,
                ip=tr.select('td')[0].text,
                port=tr.select('td')[1].text
            )
            print(item)
            proxy_list.append(item)
            try:
                Proxy.objects.create(**item)
            except IntegrityError:
                pass
        print(len(proxy_list))

    def advanced_name_ru(self, *agrs, **kwargs):
        source = 'advanced.name'
        url = 'https://advanced.name/ru/freeproxy?type=https'
        response = requests.get(url, headers=self.headers, timeout=3)
        _html = BeautifulSoup(response.content, 'html.parser')
        proxy_list = []
        for tr in _html.select('table#table_proxies tbody tr'):
            print(tr)
            item = dict(
                source=source,
                ip=tr.select('td')[1].text,
                port=tr.select('td')[2].text
            )
            print(item)
            proxy_list.append(item)
            try:
                Proxy.objects.create(**item)
            except IntegrityError:
                pass
        print(len(proxy_list))

    def free_proxy_cz(self, *agrs, **kwargs):
        source = 'free-proxy.cz'
        url = 'http://free-proxy.cz/ru/proxylist/country/all/https/ping/all'
        for page in range(1, 6):
            response = requests.get(url, headers=self.headers, timeout=3)
            _html = BeautifulSoup(response.content, 'html.parser')
            proxy_list = []
            for tr in _html.select('table#proxy_list tbody tr'):
                print(tr)
                item = dict(
                    source=source,
                    ip=tr.select('td')[0].text,
                    port=tr.select('td')[1].select('span.fport').text
                )
                print(item)
                proxy_list.append(item)
                try:
                    Proxy.objects.create(**item)
                except IntegrityError:
                    pass
            print(len(proxy_list))

    def freeproxylist_net(self, *agrs, **kwargs):
        source = 'free-proxy-list.net'
        url = 'https://free-proxy-list.net/'
        response = requests.get(url, headers=self.headers, timeout=3)
        _html = BeautifulSoup(response.content, 'html.parser')
        proxy_list = []
        for tr in _html.select('table.table.table-striped.table-bordered tbody tr'):
            if tr.select('td')[6].text == 'yes':
                item = dict(
                    source=source,
                    ip=tr.select('td')[0].text,
                    port=tr.select('td')[1].text
                )
                print(item)
                proxy_list.append(item)
                try:
                    Proxy.objects.create(**item)
                except IntegrityError:
                    pass
        print(len(proxy_list))

    def freeproxylist_ru(self):
        source = 'freeproxylist.ru'
        url = 'https://freeproxylist.ru/protocol/https'
        for page in range(1, 7):
            response = requests.get(url, headers=self.headers, timeout=3, params={'page': page})
            # print(response)
            _html = BeautifulSoup(response.content, 'html.parser')
            proxy_list = []
            for tr in _html.select('div.table-wrapper tbody.table-proxy-list tr'):
                item = dict(
                    source=source,
                    ip=tr.select('th.w-30.tblport')[0].text,
                    port=tr.select('td.w-10.tblport')[0].text
                )
                print(item)
                proxy_list.append(item)
                try:
                    Proxy.objects.create(**item)
                except IntegrityError:
                    pass
            print(len(proxy_list))

    def checkerproxy_net(self):
        source = 'checkerproxy.net'
        url = 'https://hidemy.name/ru/proxy-list/?type=s#list'
        response = requests.get(url, headers=self.headers, timeout=3)
        _html = BeautifulSoup(response.content, 'html.parser')
        print(_html)
        proxy_list = []
        for tr in _html.select('table#resultTable tbody tr'):
            print(tr)
            # item = dict(
            #     source=source,
            #     ip=tr.select('td.w-30.tblport')[0].text,
            #     port=tr.select('td.w-10.tblport')[0].text
            # )
            # print(item)
            # proxy_list.append(item)
            # try:
            #     Proxy.objects.create(**item)
            # except IntegrityError:
            #     pass
        print(len(proxy_list))

    def check(self):
        url = 'https://crm.pravkaatlanta.ru/ipcheck/'
        now = datetime.datetime.now() - datetime.timedelta(minutes=5)
        proxies_qs = Proxy.objects.filter(Q(delay=None) | Q(updated_at__lt=now))
        count = proxies_qs.count()
        response = requests.get(url=url, headers=self.headers)
        my_ip = response.json().get('ip')
        print('my_ip', my_ip)
        for proxy in proxies_qs:
            proxies = {'https': f'https://{proxy.ip}:{proxy.port}'}
            count -= 1
            try:
                start = time.time()
                response = requests.get(url=url, headers=self.headers, proxies=proxies, timeout=3)
                response_ip = response.json().get('ip')
                end = time.time()
                delay = round((end - start), 2)
                if response_ip != my_ip and delay < 2:
                    print(f'{count} {response_ip} {delay}')
                    proxy.anonymous = True
                    proxy.delay = delay
                    proxy.save()
            except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ConnectTimeout,
                    requests.exceptions.ProxyError
            ):
                print(f'{count} {proxy.ip} error')
                proxy.delete()
                continue
