from django import forms
from django.core.validators import RegexValidator
from financial_companion.models import User
from typing import Any


class UserSignUpForm(forms.ModelForm):
    """Form to register users"""

    class Meta:
        model: User = User
        fields: list[str] = [
            'first_name',
            'last_name',
            'username',
            'email',
            'bio',
            'profile_picture']
        widgets: dict[str: Any] = {'bio': forms.Textarea()}

    new_password: forms.CharField = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    password_confirmation: forms.CharField = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password: str = self.cleaned_data.get('new_password')
        password_confirmation: str = self.cleaned_data.get(
            'password_confirmation')
        if new_password != password_confirmation:
            self.add_error(
                'password_confirmation',
                'Confirmation does not match password.')

    def save(self):
        """Create a new user."""
        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            bio=self.cleaned_data.get('bio'),
            password=self.cleaned_data.get('new_password'),
            profile_picture=self.cleaned_data.get('profile_picture')
        )
        return user
