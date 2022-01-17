from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, Secondary_Role
from .models import CustomUser

# Register your models here.
class Role_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Role

admin.site.register(Role, Role_Admin)

class Secondary_Role_Admin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Secondary_Role

admin.site.register(Secondary_Role, Secondary_Role_Admin)

class CustomUser_Admin(UserAdmin):
	list_display = ('id', 'username','first_name', 'last_name', 'full_name','user_dropped','email',
					'role','is_signed_in', 'jitsi_signed_in', 'is_approved',
					'is_admin','is_staff')
	search_fields = ('id', 'email', 'username', 'role__name', 'full_name')
	readonly_fields=('id', 'date_joined', 'last_updated')

	filter_horizontal = ()
	list_filter = ('user_dropped','role', 'is_signed_in', 'jitsi_signed_in',)
	fieldsets = ()

	class Meta:
		model = CustomUser

admin.site.register(CustomUser, CustomUser_Admin)

