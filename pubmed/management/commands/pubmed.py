import random
import threading
import time
from threading import BoundedSemaphore

from django.core.management.base import BaseCommand

from pubmed.parser import ParserPubmed
from pubmed.parser.proxy_master import ProxyMaster
from ...models import Article


class Command(BaseCommand):
    help = 'Parser for pubmed'
    size = 25

    def handle(self, *args, **options):
        proxy_master = ProxyMaster()
        Article.objects.all().delete()
        start = time.time()

        thread_list = []

        ids = [i for i in range(1, 10001)]
        groups = [i for i in range(0, len(ids), self.size)]
        ids_groups = [ids[i:i+self.size] for i in groups]
        for group in ids_groups:
            for pm_id in group:
                thr = threading.Thread(target=self.parse, args=(proxy_master, pm_id,))
                thread_list.append(thr)
                thr.start()
            for thr in thread_list:
                thr.join()
            print(' ')
            # time.sleep(2)

        ParserPubmed().end()
        end = time.time()
        print(end - start)

    def parse(self, proxy_master, pm_id):
        pool = BoundedSemaphore(value=self.size)

        with pool:
            # print(f'{threading.current_thread().name}: - {pm_id}', proxy['string'])
            ParserPubmed().parse(pm_id)
