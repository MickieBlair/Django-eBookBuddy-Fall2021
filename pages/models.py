from django.db import models

# Create your models here.

class Update_In_Progress(models.Model):
	name = models.CharField(max_length=100, null=True, blank=True, unique=True)
	updating = models.BooleanField(default=False)
	date_created = models.DateTimeField(verbose_name='date created', auto_now_add=True)
	last_updated = models.DateTimeField(verbose_name='last updated', auto_now=True)
	
	class Meta:
		ordering = ['id']
		verbose_name = 'Update In Progress'
		verbose_name_plural = 'Update In Progress'

	def __str__(self):
		return self.name