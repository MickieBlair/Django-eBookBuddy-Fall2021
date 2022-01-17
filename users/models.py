from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from rest_framework.authtoken.models import Token
from users import jwt_token


# Create your models here.
class Role(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Role'
		verbose_name_plural = 'Roles'

	def __str__(self):
		return self.name

class Secondary_Role(models.Model):
	name = models.CharField(max_length=100, null=False, blank=False, unique=True)
	class Meta:
		ordering = ['id']
		verbose_name = 'Secondary Role'
		verbose_name_plural = 'Secondary Role'

	def __str__(self):
		return self.name

class CustomAccountManager(BaseUserManager):
	def create_superuser(self, email, username, password, **other_fields):
		other_fields.setdefault('is_staff', True)
		other_fields.setdefault('is_superuser', True)
		other_fields.setdefault('is_active', True)
		other_fields.setdefault('is_approved', True)
		other_fields.setdefault('is_admin', True)
		other_fields.setdefault('is_active', True)
		other_fields.setdefault('is_signed_in', False)
		other_fields.setdefault('jitsi_signed_in', False)

		if other_fields.get('is_staff') is not True:
			raise ValueError('Superuser must be assigned to is_staff=True.')

		if other_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must be assigned to is_superuser=True.')

			

		return self.create_user(email, username, password, **other_fields)

	def create_user(self, email, username, password, **other_fields):

		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		email = self.normalize_email(email)
		user = self.model(email=email, username=username, **other_fields)
		user.set_password(password)
		user.save()
		return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
	first_name = models.CharField(max_length=150, null=False, blank=False)
	middle_name = models.CharField(max_length=150, blank=True)
	last_name = models.CharField(max_length=150, null=False, blank=False)
	full_name = models.CharField(max_length=150, null=True, blank=True)
	username = models.CharField(max_length=150, unique=True)
	email = models.EmailField(verbose_name="email", max_length=80,
							unique=False, null=False, blank=False)
	role = models.ForeignKey(Role, on_delete=models.CASCADE,
								related_name='user_role', null=True, blank=True)
	secondary_roles = models.ManyToManyField(Secondary_Role,
								related_name='roles', blank=True)
	is_approved = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser= models.BooleanField(default=False)	
	is_signed_in = models.BooleanField(default=False)
	jitsi_signed_in = models.BooleanField(default=False)
	user_dropped = 	models.BooleanField(default=False)
	date_joined	= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_updated = models.DateTimeField(verbose_name='last updated', auto_now=True)
	avatar_img = models.ImageField(upload_to='avatars', null=True, blank=True)
	objects = CustomAccountManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email']

	def __str__(self):
		return self.username

	def profile(self):
		if self.role:
			if self.role.name == "Staff":
				return self.staff_profile
			elif self.role.name == "Student":
				return self.student_profile
			elif self.role.name == "Volunteer":
				return self.volunteer_profile
		else:
			return None

	def meeting_token(self):
		if self.role.name == "Staff" or self.role.name == "Volunteer":
			affiliation = "teacher"
		else:
			affiliation = "student"
		return jwt_token.generateUserToken(self.username, self.email, affiliation)

	def new_meeting_token(self):
		return jwt_token.generateBaseToken(self.username, self.email, self.role.name, self.avatar_img)

	class Meta:
		ordering = ['id']
		verbose_name = 'User'
		verbose_name_plural = 'Users'

@receiver(pre_save, sender=CustomUser)
def auto_populate_full_name(sender, instance=None, created=False, **kwargs):
	full_name = ""
	if instance.first_name:
		full_name = full_name + instance.first_name
	if instance.middle_name:
		full_name = full_name + " " + instance.middle_name 
	if instance.last_name:
		full_name = full_name + " " + instance.last_name
	instance.full_name = full_name

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)


