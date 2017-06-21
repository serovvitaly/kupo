from django.contrib import admin
from spider.models import OfferUrl, OfferProvider

class OfferUrlAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['id', 'url_link', 'offer_provider', 'created_at', 'is_supervised']
    list_filter = ['offer_provider', 'is_supervised']

    def url_link(self, rec):
        return '<a target="_blank" href="'+rec.url+'">'+rec.url+'</a>'
    url_link.allow_tags = True


class OfferProviderAdmin(admin.ModelAdmin):
    ordering = ['title']
    list_per_page = 20
    list_display = ['title', 'damail_link', 'affiliate_program_link', 'provider']

    def damail_link(self, rec):
        return '<a target="_blank" href="'+rec.domain+'">'+rec.domain+'</a>'
    damail_link.allow_tags = True

    def affiliate_program_link(self, rec):
        if rec.affiliate_program_url == '':
            return ''
        return '<a target="_blank" href="'+rec.affiliate_program_url+'">Партнерская программа</a>'
    affiliate_program_link.allow_tags = True


admin.site.register(OfferUrl, OfferUrlAdmin)
admin.site.register(OfferProvider, OfferProviderAdmin)
