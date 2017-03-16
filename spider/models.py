from django.db import models


class OfferUrl(models.Model):
    class Meta:
        db_table = 'offer_url'
    url = models.TextField()
    offer_provider = models.ForeignKey('OfferProvider')
    is_supervised = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)


class OfferProvider(models.Model):
    class Meta:
        db_table = 'offer_provider'
    title = models.CharField(max_length=300)
    domain = models.CharField(max_length=100, default='', blank=True)
    provider = models.CharField(max_length=300)
    affiliate_program_url = models.CharField(max_length=200, default='', blank=True)
    affiliate_program_conditions = models.TextField(blank=True)

    def __str__(self):
        return self.title


class ContentProvider(models.Model):
    class Meta:
        db_table = 'content_provider'
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=800)

