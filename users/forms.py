from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from users.models import CustomUser



class Create_User_Form(UserCreationForm):
	email = forms.EmailField(max_length=254, help_text='Required. Add a valid email address.')

	class Meta:
		model = CustomUser
		fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'is_approved' )

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			existing_account = CustomUser.objects.exclude(pk=self.instance.pk).get(username=username)
		except CustomUser.DoesNotExist:
			return username
		raise forms.ValidationError('Username "%s" is already in use.' % username)


class AccountAuthenticationForm(forms.ModelForm):

	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	class Meta:
		model = CustomUser
		fields = ('username', 'password')

	def clean(self):
		if self.is_valid():
			username = self.cleaned_data['username']
			password = self.cleaned_data['password']
			if not authenticate(username=username, password=password):
				raise forms.ValidationError("Invalid login")


class User_Update_Form(forms.ModelForm):

	class Meta:
		model = CustomUser
		fields = ('first_name', 'middle_name', 'last_name','username', 'email')

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			account = CustomUser.objects.exclude(pk=self.instance.pk).get(username=username)
		except CustomUser.DoesNotExist:
			return username
		raise forms.ValidationError('Username "%s" is already in use.' % username)