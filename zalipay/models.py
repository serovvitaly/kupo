from django.db import models
from django.contrib.postgres.fields import JSONField


class ZalipayRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'zalipay':
            return 'zalipay'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'zalipay':
            return 'zalipay'
        return None


class Post(models.Model):
    class Meta:
        db_table = 'documents'
    title = models.CharField(max_length=300)
    content = models.TextField()
    meta_data = JSONField()
    ribbon = models.ForeignKey('Ribbon')


class Ribbon(models.Model):
    class Meta:
        db_table = 'ribbons'
    title = models.CharField(max_length=300)

    def __str__(self):
        return self.title