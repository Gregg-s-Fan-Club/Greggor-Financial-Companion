from django import forms
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from typing import Any
from .test_form_base import FormTestCase
from financial_companion.forms import UserSignUpForm
from financial_companion.models import User


class SignUpFormTestCase(FormTestCase):
    """Unit tests of the sign up form"""

    def setUp(self):
        super().setUp()
        self.url: str = reverse('sign_up')
        self.form_input: dict[str, Any] = {
            "first_name": "John",
            "last_name": "Smith",
            "username": "@johnsmith",
            "email": "johnsmith@example.org",
            "bio": "John Smith's Personal Spending Tracker",
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_valid_sign_up_form(self):
        form: UserSignUpForm = UserSignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form: UserSignUpForm = UserSignUpForm()
        self._assert_form_has_necessary_fields(
            form,
            'first_name',
            'last_name',
            'username',
            'email',
            'bio',
            'new_password',
            'password_confirmation'
        )
        email_field: forms.EmailField = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        new_password_widget: forms.PasswordInput = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        password_confirmation_widget: forms.PasswordInput = form.fields[
            'password_confirmation'].widget
        self.assertTrue(
            isinstance(
                password_confirmation_widget,
                forms.PasswordInput))

    def test_form_uses_model_validation(self):
        self.form_input['username']: str = 'badusername'
        form: UserSignUpForm = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password']: str = 'password123'
        self.form_input['password_confirmation']: str = 'password123'
        form: UserSignUpForm = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password']: str = 'PASSWORD123'
        self.form_input['password_confirmation']: str = 'PASSWORD123'
        form: UserSignUpForm = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password']: str = 'PasswordABC'
        self.form_input['password_confirmation']: str = 'PasswordABC'
        form: UserSignUpForm = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation']: str = 'WrongPassword123'
        form: UserSignUpForm = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form: UserSignUpForm = UserSignUpForm(data=self.form_input)
        before_count: int = User.objects.count()
        form.save()
        after_count: int = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        user: User = User.objects.get(username='@johnsmith')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Smith')
        self.assertEqual(user.email, "johnsmith@example.org")
        self.assertEqual(user.bio, "John Smith's Personal Spending Tracker")
        is_password_correct: bool = check_password(
            'Password123', user.password)
        self.assertTrue(is_password_correct)
