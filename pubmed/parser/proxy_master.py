import time
from pubmed.models import Proxy


class ProxyMaster:
    __instance = None
    proxies = []

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __del__(self):
        self.__instance = None

    def __init__(self, _len=None):
        if not self.proxies:
            qs = Proxy.objects.filter(delay__lt=2).order_by('delay')
            print(f'ProxyMaster.__init__() proxies:{qs.count()}')
            if _len:
                qs = qs[0:_len]
            for proxy in qs:
                self.proxies.append(dict(
                    string=f'{proxy.ip}:{proxy.port}',
                    ip=proxy.ip,
                    port=proxy.port,
                    started=0,
                    time=0,
                    count=0,
                ))

    def get(self):
        _proxies = filter(lambda i: not i['started'], self.proxies)  # Фильтруем по ключу 'started'
        _proxy = sorted(_proxies, key=lambda i: i['count'])[0]  # Сортируем по ключу 'count'
        _proxy['started'] = time.time()
        return _proxy

    def skip(self, proxy):
        _proxy = next(i for i in self.proxies if i == proxy)
        _proxy['time'] += time.time() - _proxy['started']
        _proxy['started'] = 0
        _proxy['count'] += + 1
        return _proxy

    def stat(self):
        return dict(
            time=sum(i['time'] for i in self.proxies),
            count=sum(i['count'] for i in self.proxies)
        )
