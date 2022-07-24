from django.contrib import admin
from store.admin import ProductAdmin
from tags.models import TaggedItem
from store.models import Product
from django.contrib.contenttypes.admin import GenericTabularInline
# Register your models here.


class TagInLine(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInLine]

admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)