from django.urls import reverse
from .test_view_base import ViewTestCase
from financial_companion.models import User, CategoryTarget
from django.http import HttpResponse
from django.contrib.messages.storage.base import Message


class DeleteCategoryTargetViewTestCase(ViewTestCase):
    """Tests of the delete category target view."""

    def setUp(self) -> None:
        super().setUp()
        self.url: str = reverse('delete_category_target', kwargs={"pk": 1})
        self.user: User = User.objects.get(username='@johndoe')

    def test_delete_category_target_url(self) -> None:
        self.assertEqual(self.url, '/delete_target/category/1')

    def test_successful_deletion(self) -> None:
        self._login(self.user)
        before_count: int = CategoryTarget.objects.count()
        response: HttpResponse = self.client.get(self.url, follow=True)
        after_count: int = CategoryTarget.objects.count()
        self.assertEqual(after_count + 1, before_count)
        self.assertTemplateUsed(response, 'pages/individual_category.html')
        messages_list: list[Message] = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)

    def test_user_tries_to_delete_someone_elses_category_target(self) -> None:
        self._login(self.user)
        self.url: str = reverse('delete_category_target', kwargs={"pk": 6})
        response_url: str = reverse(
            "categories_list", kwargs={
                "search_name": "all"})
        response: HttpResponse = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            response_url,
            status_code=302,
            target_status_code=200)
        self.assertTemplateUsed(response, 'pages/category_list.html')

    def test_user_provides_invalid_pk(self) -> None:
        self._login(self.user)
        self.url: str = reverse('delete_category_target', kwargs={"pk": 300})
        response_url: str = reverse("dashboard")
        response: HttpResponse = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            response_url,
            status_code=302,
            target_status_code=200)
        self.assertTemplateUsed(response, 'pages/dashboard.html')

    def test_get_view_redirects_when_not_logged_in(self) -> None:
        self._assert_require_login(self.url)
