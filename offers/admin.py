from django.contrib import admin
from offers.models import Offer, Source, MerchantModel, MerchantReviewSource


class OfferAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['title', 'status']
    #list_filter = ['offer_provider', 'is_supervised']

    def url_link(self, rec):
        return '<a target="_blank" href="'+rec.url+'">'+rec.url+'</a>'
    url_link.allow_tags = True


class MerchantAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['name', 'site_url', 'original_system', 'url_link']
    list_filter = ['original_system']

    def url_link(self, rec):
        return '<a href="/admin/offers/merchantreviewsource/?merchant__id__exact='+str(rec.id)+'">Ресурсы</a>'
    url_link.allow_tags = True


class SourceAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['title', 'system_name']


class MerchantReviewSourceAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['title', 'url', 'source_type', 'merchant']
    list_filter = ['source_type']

admin.site.register(Offer, OfferAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(MerchantModel, MerchantAdmin)
admin.site.register(MerchantReviewSource, MerchantReviewSourceAdmin)