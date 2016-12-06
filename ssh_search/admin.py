from django.contrib import admin

from ssh_search.models import SiteUser, SocialLogin
# Register your models here.

# admin.site.register(User)
@admin.register(SiteUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('_id', 'email', 'first_name', 'last_name', 'session_id')

# admin.site.register(SocialLogin)
@admin.register(SocialLogin)
class SocialLogin(admin.ModelAdmin):
    list_display = ('_id', 'user_id', 'site_name', 'auth_token')
    list_filter = ('site_name', 'user_id')
