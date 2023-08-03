from django.db import models


class Article(models.Model):
    """
        Статьи pubmed
    """

    id = models.BigAutoField('Pubmed ID', primary_key=True)
    title = models.TextField('Title', null=True)
    error = models.TextField('Title', null=True)
    data = models.JSONField(null=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        default_permissions = ()
        permissions = []


class Proxy(models.Model):
    """
        Список проксей
    """
    ip = models.CharField(primary_key=True, max_length=128)
    port = models.IntegerField(null=True)
    delay = models.FloatField(null=True)
    source = models.CharField(max_length=256)

    updated_at = models.DateTimeField(auto_now=True)

    # created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Прокси'
        verbose_name_plural = 'Прокси'
        default_permissions = ()
        permissions = []

    def __str__(self):
        return '%s:%s (%s)' % (self.ip, self.port, self.delay)
