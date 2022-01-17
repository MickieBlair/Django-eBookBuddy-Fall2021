from django.contrib import admin

from pages.models import Update_In_Progress

# Register your models here.
class Update_In_Progress_Admin(admin.ModelAdmin):
	list_display = ('name', 'updating')
	search_fields = ('name',)
	readonly_fields=()
	filter_horizontal = ()

	class Meta:
		model = Update_In_Progress

admin.site.register(Update_In_Progress, Update_In_Progress_Admin)

