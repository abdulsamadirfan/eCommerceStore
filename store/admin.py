# from tags.models import TaggedItem
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from . import models
from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse

 
class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)






# class TagInLine(GenericTabularInline):
#     autocomplete_fields = ['tag']
#     model = TaggedItem



# Register your models here.
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):

    search_fields = ['title']
    autocomplete_fields = ['collection']
    # exclude = ['promotions'] # similatly "fields", "readonly_fields"
    prepopulated_fields = {
        'slug': ['title']
    }
    # inlines = [TagInLine]
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price',
                    'inventory_status', 'collection',
                    "collection_title"]
    list_editable = ['unit_price']
    list_per_page = 250
    list_filter = ['collection', 'last_update', InventoryFilter]
    # to load query already
    list_select_related = ['collection']

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return "Low"
        return "Ok"

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated',
            messages.SUCCESS)


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['first_name', 'last_name', 'membership', 'orders_count']
    list_editable = ['membership']
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    def orders_count(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))

        return format_html('<a href = "{}">{} Orders</a>', url, customer.order_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            order_count=Count('order')
        )


class OrderItemInLine(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ['product']
    extra = 0
    min_num = 1


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInLine]
    autocomplete_fields = ['customer']
    list_display = ['id', 'placed_at', 'customer']


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_count']
    search_fields = ['title']

    @admin.display(ordering="product_count")
    def product_count(self, collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            }))

        return format_html('<a href = "{}">{}</a>', url, collection.product_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('product')
        )
