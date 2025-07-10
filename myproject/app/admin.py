# Register your models here.
# app/admin.py
from django.contrib import admin
from .models import Profile,Job,JobApplication

admin.site.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')  # ✅ to show role in list view
    fields = ('user', 'role')


admin.site.register(Job)
admin.site.register(JobApplication)
