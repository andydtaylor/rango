from django.contrib import admin
from rango.models import Category, Page, UserProfile

# Register your models here.
admin.site.register(Category)

class PageAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Category', {'fields': ['category']}),
        ('Details', {'fields': ['title', 'url', 'views']}),
    ]
    list_display = ('category', 'title', 'url', 'views')
    search_fields = ['title', 'url']

admin.site.register(Page, PageAdmin)

admin.site.register(UserProfile)
