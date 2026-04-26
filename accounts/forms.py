from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Username or Email'),
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)

            if self.user_cache is None:
                UserModel = get_user_model()
                user = UserModel.objects.filter(username__iexact=username).first()
                if user is None:
                    user = UserModel.objects.filter(email__iexact=username).first()
                if user is not None:
                    self.user_cache = authenticate(
                        self.request,
                        username=user.get_username(),
                        password=password,
                    )

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
