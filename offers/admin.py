from django.contrib import admin
from offers.models import Offer

class OfferAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['title', 'status']
    #list_filter = ['offer_provider', 'is_supervised']

    def url_link(self, rec):
        return '<a target="_blank" href="'+rec.url+'">'+rec.url+'</a>'
    url_link.allow_tags = True

admin.site.register(Offer, OfferAdmin)