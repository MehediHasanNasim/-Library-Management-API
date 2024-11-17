from django.contrib import admin
from .models import *
# Register your models here.
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Optionally, customize the admin panel for the User model
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)


    # Fields to show on the user creation and edit pages
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),  # Add your custom field here
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),  # Ensure the role field is in the creation form
    )
    
    
admin.site.register(Book) 
admin.site.register(BorrowRecord) 
admin.site.register(BookReturn) 
admin.site.register(Fine) 
admin.site.register(Submission) 

