from django.core.management.base import BaseCommand
from ...parser.proxy_parser import ProxyParser


class Command(BaseCommand):
    def handle(self, *args, **options):
        ProxyParser().check()
