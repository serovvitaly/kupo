from django.db import models


class Offer(models.Model):
    class Meta:
        db_table = 'offers'
    title = models.CharField(max_length=500)
    #likes_count = models.IntegerField()
    #purchases_count = models.IntegerField()
    rules = models.TextField()
    description = models.TextField()
    expiration_date = models.DateTimeField(blank=True, null=True)
    coupon_expiration_date = models.DateTimeField()
    coupon_beginning_usage_date = models.DateTimeField()



class OfferItem(models.Model):
    class Meta:
        db_table = 'offers_items'
    title = models.CharField(max_length=500)
    purchases_count = models.IntegerField()
    purchase_url = models.CharField(max_length=500, blank=True, null=True)
    discount_value = models.FloatField()
    price_value = models.FloatField()
    offer = models.ForeignKey('Offer')

