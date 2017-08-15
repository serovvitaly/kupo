from django.db import models


STATUS_CHOICES = (
    ('d', 'Черновик'),
    ('p', 'Опубликовано'),
    ('w', 'Скрыто'),
    ('o', 'В обработке'),
)

ORIGINAL_SYSTEM_CHOICES = (
    ('bg', 'Бугага'),
)

class MerchantModel(models.Model):
    class Meta:
        db_table = 'merchants'
    name = models.CharField(max_length=300)
    site_url = models.CharField(max_length=300)
    work_hours = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=300)
    original_system = models.CharField(max_length=3, choices=ORIGINAL_SYSTEM_CHOICES, null=True)
    original_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    class Meta:
        db_table = 'sources'
    title = models.CharField(max_length=300)
    system_name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.title

class MerchantReviewSource(models.Model):
    class Meta:
        db_table = 'merchants_reviews_sources'
    title = models.CharField(max_length=300)
    url = models.CharField(max_length=300)
    source_type = models.ForeignKey(Source)
    merchant = models.ForeignKey(MerchantModel)

    def __str__(self):
        return self.title


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
    merchant = models.ForeignKey(MerchantModel)


class OfferProperty(models.Model):
    class Meta:
        db_table = 'offers_properties'
    offer = models.ForeignKey('Offer')
    type = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=300)


class OfferItemModel(models.Model):
    class Meta:
        db_table = 'offers_items'
    title = models.CharField(max_length=500)
    url = models.CharField(max_length=300)
    amount = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    discount = models.FloatField(null=True, blank=True)
    offer = models.ForeignKey('Offer')


class OfferMedia(models.Model):
    class Meta:
        db_table = 'offers_media'
    url = models.CharField(max_length=300)
    offer = models.ForeignKey('Offer')


class Place(models.Model):
    class Meta:
        db_table = 'places'
    merchant = models.ForeignKey('MerchantModel')
    offer = models.ForeignKey('Offer'),
    title = models.CharField(max_length=300),
    address = models.CharField(max_length=300),
    phones = models.CharField(max_length=300),
    latitude = models.FloatField(null=True, blank=True),
    longitude = models.FloatField(null=True, blank=True)
