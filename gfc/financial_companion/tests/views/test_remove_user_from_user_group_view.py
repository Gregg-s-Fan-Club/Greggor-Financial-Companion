from django.urls import reverse
from .test_view_base import ViewTestCase
from financial_companion.models import User, UserGroup
from django.contrib.messages.storage.base import Message
from django.http import HttpResponse


class RemoveUserFromUserGroupViewTestCase(ViewTestCase):
    """Tests of the remove user from user group view."""

    def setUp(self):
        super().setUp()
        self.url: str = reverse(
            'remove_user_from_user_group', kwargs={
                "group_pk": 1, "user_pk": 2})
        self.user: User = User.objects.get(username='@johndoe')
        self.user_two: User = User.objects.get(username='@janedoe')
        self.user_group: UserGroup = UserGroup.objects.get(pk=1)
        self.user_group.add_member(self.user)
        self.user_group.add_member(self.user_two)

    def test_remove_user_from_user_group_url(self):
        self.assertEqual(self.url, '/remove_user_from_user_group/1/2')

    def test_successful_user_removal(self):
        self._login(self.user)
        before_count: int = self.user_group.members.count()
        response: HttpResponse = self.client.get(self.url, follow=True)
        after_count: int = self.user_group.members.count()
        self.assertEqual(after_count, before_count - 1)
        self.assertTemplateUsed(response, 'pages/individual_group.html')
        messages_list: list[Message] = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_unsuccessful_user_removal_due_to_invalid_group_pk(self):
        self._login(self.user)
        url: str = reverse(
            'remove_user_from_user_group',
            kwargs={
                "group_pk": 1000,
                "user_pk": 2})
        before_count: int = self.user_group.members.count()
        response: HttpResponse = self.client.get(url, follow=True)
        after_count: int = self.user_group.members.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'pages/all_groups.html')
        messages_list: list[Message] = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_unsuccessful_user_removal_due_to_invalid_user_pk(self):
        self._login(self.user)
        url: str = reverse(
            'remove_user_from_user_group',
            kwargs={
                "group_pk": 1,
                "user_pk": 1000})
        before_count: int = self.user_group.members.count()
        response: HttpResponse = self.client.get(url, follow=True)
        after_count: int = self.user_group.members.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'pages/individual_group.html')
        messages_list: list[Message] = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_unsuccessful_user_removal_due_to_user_not_being_a_member_of_user_group(
            self):
        self._login(self.user)
        self.user_group.remove_member(self.user_two)
        url: str = reverse(
            'remove_user_from_user_group',
            kwargs={
                "group_pk": 1,
                "user_pk": 2})
        before_count: int = self.user_group.members.count()
        response: HttpResponse = self.client.get(url, follow=True)
        after_count: int = self.user_group.members.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'pages/individual_group.html')
        messages_list: list[Message] = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_unsuccessful_user_removal_due_to_request_user_not_the_owner_of_user_group(
            self):
        self._login(self.user_two)
        before_count: int = self.user_group.members.count()
        response: HttpResponse = self.client.get(self.url, follow=True)
        after_count: int = self.user_group.members.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, 'pages/all_groups.html')
        messages_list: list[Message] = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
