from django.contrib import admin
from .models import ContactMessage, EmploymentApplication

# Register your models here.
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    
@admin.register(EmploymentApplication)
class EmploymentApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'position', 'experience', 'created_at')
    list_filter = ('position', 'experience', 'created_at')
    search_fields = ('name', 'email', 'cover_letter')
    readonly_fields = ('created_at',)
