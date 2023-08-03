import time

import requests
from lxml import html

from ..models import Article
from ..parser.proxy_master import ProxyMaster


class ParserPubmed:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={}'
    page_paths = dict(
        # id=['//pmid'],
        title=['//articletitle', '//booktitle']
    )

    def parse(self, pm_id):
        proxy_master = ProxyMaster()
        proxy = proxy_master.get()
        proxies = {'https': 'https://%s:%s' % (proxy['ip'], proxy['port'])}
        try:
            response = requests.get(self.url.format(pm_id), headers=self.headers, proxies=proxies, timeout=5)
        except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout
        ) as error:
            PubmedCollect().error(pm_id, proxy['ip'], error)
            print(pm_id, 'error', proxy['ip'])
            return False
        finally:
            proxy_master.skip(proxy)

        # print(pm_id, response.status_code)
        tree = html.fromstring(response.content)
        pm_dict = self.get_dict(pm_id, tree)
        print(pm_dict)
        PubmedCollect().insert(pm_dict)
        # Article.objects.get_or_create(**pm_dict)
        return True

    def get_dict(self, pm_id, tree):
        _data = dict(id=pm_id)
        for key, paths in self.page_paths.items():
            for path in paths:
                _data[key] = ' '.join([i.text for i in tree.xpath(path)])
                if _data[key]:
                    break

        return dict(**_data)

    @staticmethod
    def end():
        PubmedCollect().end()
        return True


class PubmedCollect:
    __instance = None
    articles = []
    errors = []

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __del__(self):
        self.__instance = None

    def __init__(self):
        pass

    def insert(self, article):
        self.articles.append(article)
        if len(self.articles) > 100:
            _articles = self.articles.copy()
            self.articles = []
            Article.objects.bulk_create([Article(**i) for i in _articles])

    def error(self, pm_id, proxy, error):
        self.errors.append(dict(
            id=pm_id,
            error=f'[{proxy}] {error}'
        ))
        if len(self.errors) > 100:
            _errors = self.errors.copy()
            self.errors = []
            Article.objects.bulk_create([Article(**i) for i in self.errors])

    def end(self):
        time.sleep(3)
        Article.objects.bulk_create([Article(**i) for i in self.articles])
        Article.objects.bulk_create([Article(**i) for i in self.errors])
