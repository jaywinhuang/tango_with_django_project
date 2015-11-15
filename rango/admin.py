from django.contrib import admin
from rango.models import Category, Page, UserProfile

class PageAdmin(admin.ModelAdmin):
    list_display = ('id','title','category','url','views')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'slug', 'views' ,'likes')
    prepopulated_fields = {'slug':('name',)}

# Register your models here.

admin.site.register(Category,CategoryAdmin)
admin.site.register(Page,PageAdmin)
admin.site.register(UserProfile)



