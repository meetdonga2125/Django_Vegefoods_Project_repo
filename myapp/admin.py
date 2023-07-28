from django.contrib import admin
from .models import User,Fruitage,Wishlist,Cart

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display=('fname','address', 'mobile')
    search_fields=('fname',)

class FruitageAdmin(admin.ModelAdmin):
    list_display=('seller', 'fruitage_category', 'fruitage_name', 'fruitage_price')
    search_fields=('fruitage_name',)    


admin.site.register(User,UserAdmin)
admin.site.register(Fruitage,FruitageAdmin)
admin.site.register(Wishlist)
admin.site.register(Cart)