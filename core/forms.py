from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
  class Meta:
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

from django.contrib.auth.forms import AuthenticationForm
from django_recaptcha.fields import ReCaptchaField

class CaptchaAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField()
  