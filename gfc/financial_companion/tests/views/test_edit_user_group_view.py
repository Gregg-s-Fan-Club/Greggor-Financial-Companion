from django.urls import reverse
from .test_view_base import ViewTestCase
from financial_companion.forms import UserGroupForm
from financial_companion.models import User, UserGroup
from django.http import HttpResponse
from django.contrib.messages.storage.base import Message
from typing import Any


class EditUserGroupViewTestCase(ViewTestCase):
    """Tests of the edit user group view."""

    def setUp(self) -> None:
        super().setUp()
        self.url: str = reverse('edit_user_group', kwargs={"pk": 1})
        self.form_input: dict[str, Any] = {
            'name': 'Financial Club',
            'description': 'We are the best financial club',
        }
        self.user: User = User.objects.get(username='@johndoe')
        self.group: UserGroup = UserGroup.objects.get(invite_code='ABCDEFGH')
        self.group.add_member(self.user)

    def test_edit_user_group_url(self) -> None:
        self.assertEqual(self.url, '/edit_user_group/1')

    def test_get_edit_user_group(self) -> None:
        self._login(self.user)
        response: HttpResponse = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/create_user_group.html')
        form: UserGroupForm = response.context['form']
        self.assertTrue(isinstance(form, UserGroupForm))
        self.assertFalse(form.is_bound)
        messages_list: list[Message] = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_unsuccessful_edit_user_group_form_submission(self) -> None:
        self._login(self.user)
        response: HttpResponse = self.client.get(self.url)
        self.form_input['name']: str = ''
        before_count: int = UserGroup.objects.count()
        response: HttpResponse = self.client.post(self.url, self.form_input)
        after_count: int = UserGroup.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/create_user_group.html')
        form: UserGroupForm = response.context['form']
        self.assertTrue(isinstance(form, UserGroupForm))

    def test_successful_edit_user_group_form_submission(self) -> None:
        self._login(self.user)
        before_count: int = UserGroup.objects.count()
        response: HttpResponse = self.client.post(
            self.url, self.form_input, follow=True)
        after_count: int = UserGroup.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'pages/individual_group.html')

    def test_successful_edit_user_group_form_submission_when_group_picture_is_false(
            self) -> None:
        self._login(self.user)
        before_count: int = UserGroup.objects.count()
        self.form_input['group_picture']: bool = False
        response: HttpResponse = self.client.post(
            self.url, self.form_input, follow=True)
        after_count: int = UserGroup.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'pages/individual_group.html')

    def test_user_tries_to_edit_someone_elses_user_group(self) -> None:
        self._login(self.user)
        self.url: str = reverse('edit_user_group', kwargs={"pk": 2})
        response_url: str = reverse(
            "all_groups_redirect")
        response: HttpResponse = self.client.post(
            self.url, self.form_input, follow=True)
        self.assertRedirects(
            response,
            response_url,
            status_code=302,
            target_status_code=200)
        self.assertTemplateUsed(response, 'pages/all_groups.html')

    def test_user_provides_invalid_pk(self) -> None:
        self._login(self.user)
        self.url: str = reverse('edit_user_group', kwargs={"pk": 300})
        response_url: str = reverse(
            "all_groups_redirect")
        response: HttpResponse = self.client.post(
            self.url, self.form_input, follow=True)
        self.assertRedirects(
            response,
            response_url,
            status_code=302,
            target_status_code=200)
        self.assertTemplateUsed(response, 'pages/all_groups.html')

    def test_get_view_redirects_when_not_logged_in(self) -> None:
        self._assert_require_login(self.url)
