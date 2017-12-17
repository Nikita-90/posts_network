from django import forms
from django.conf import settings
# from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .widgets import AdminDateInputWidget
from . models import CustomUser


class BaseUserForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseUserForm, self).__init__(*args, **kwargs)
        # adding css classes to widgets without define the fields:
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label
            self.fields[field].label = ''
            self.fields[field].help_text = ''


class LoginForm(BaseUserForm, forms.Form):
    email = forms.EmailField(label="Email address", max_length=255)
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': "Please enter a correct %(username)s and password. "
                         "Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive.",
    }

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            try:
                self.user_cache = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise forms.ValidationError('Password or email is incorrect.', code='invalid_login')
            if not self.user_cache.check_password(password):
                raise forms.ValidationError('Password or email is incorrect.', code='invalid_login')


class UserCreationForm(forms.ModelForm, BaseUserForm):
    birthday = forms.DateTimeField(widget=AdminDateInputWidget, label='Birthday')
    password1 = forms.CharField(min_length=6, max_length=50, label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=6, max_length=50, label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'country', 'city', 'birthday', 'is_active')

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['country'].required = True
        self.fields['city'].required = True
        self.fields['is_active'].widget = self.fields['is_active'].hidden_widget()

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True, request=None):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

        if user.has_usable_password():
            data_message = {
                'host': request.get_raw_uri(),
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }
            subject = "Post Network"
            message = loader.render_to_string('common/password_complete_message.txt', data_message)
            to = (user.email,)
            send_mail(subject, message, settings.EMAIL_HOST_USER, to)

        return user