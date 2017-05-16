from django.contrib import admin
from zalipay.models import Post, Ribbon


class PostAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['title']


class RibbonAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['title']


admin.site.register(Post, PostAdmin)
admin.site.register(Ribbon, RibbonAdmin)

