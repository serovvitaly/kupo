from django.db import models


STATUS_CHOICES = (
    ('d', 'Черновик'),
    ('p', 'Опубликовано'),
    ('w', 'Скрыто'),
    ('o', 'В обработке'),
)


class Offer(models.Model):
    class Meta:
        db_table = 'offers'
    url = models.CharField(max_length=500, unique=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    likes_count = models.IntegerField(blank=True, null=True)
    purchases_count = models.IntegerField(blank=True, null=True)
    rules = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    expiration_date = models.DateTimeField(blank=True, null=True)
    coupon_expiration_date = models.DateTimeField(blank=True, null=True)
    coupon_beginning_usage_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, null=True, default='o')
    merchant = models.ForeignKey('Merchant', null=True, blank=True)


class OfferProperty(models.Model):
    class Meta:
        db_table = 'offers_properties'
    offer = models.ForeignKey('Offer')
    type = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=300)


class OfferItem(models.Model):
    class Meta:
        db_table = 'offers_items'
    title = models.CharField(max_length=500)
    #purchases_count = models.IntegerField()
    purchase_url = models.CharField(max_length=300, blank=True, null=True)
    discount_value = models.FloatField()
    price_value = models.FloatField()
    offer = models.ForeignKey('Offer')


class OfferMedia(models.Model):
    class Meta:
        db_table = 'offers_media'
    url = models.CharField(max_length=300)
    offer = models.ForeignKey('Offer')


class Merchant(models.Model):
    class Meta:
        db_table = 'merchants'
    name = models.CharField(max_length=300)
    site_url = models.CharField(max_length=300)
    work_hours = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=300)


class Place(models.Model):
    class Meta:
        db_table = 'places'
    merchant = models.ForeignKey('Merchant')
    data = models.TextField()
