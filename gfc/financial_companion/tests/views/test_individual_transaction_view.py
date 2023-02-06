from .test_view_base import ViewTestCase
from financial_companion.models import User, Account, PotAccount, BankAccount, Transaction
from django.http import HttpResponse
from django.urls import reverse

class IndividualTransactionViewTestCase(ViewTestCase):
    """Unit tests of the individual transaction view"""

    def setUp(self):
        self.user: User = User.objects.get(username="@johndoe")
        self.transaction: Transaction = Transaction.objects.get(id=4)
        self.url: str = reverse("individual_transaction", kwargs={"pk": self.transaction.id})

    def test_valid_individual_transaction_url(self):
        self.assertEqual(self.url, f"/individual_transaction/{self.transaction.id}/")

    def test_valid_get_view_individual_transaction(self):
        self._login(self.user)
        response: HttpResponse = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/individual_transaction.html")
        transaction: Transaction = response.context["transaction"]
        self.assertTrue(isinstance(transaction, Transaction))
        self.assertContains(response, self.transaction.title.capitalize())
        self.assertContains(response, self.transaction.description)
        self.assertContains(response, self.transaction.category.name.capitalize())
        self.assertContains(response, self.transaction.amount)
        self.assertContains(response, self.transaction.currency.upper())
        self.assertContains(response, self.transaction.sender_account.name.capitalize())
        self.assertContains(response, self.transaction.receiver_account.name.capitalize())

    def test_invalid_transaction_does_not_exist(self):
        self._login(self.user)
        url: str = reverse("individual_transaction", kwargs={"pk": self.transaction.id+99999999})
        response: HttpResponse = self.client.get(url, follow=True)
        response_url: str = reverse("dashboard")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "pages/dashboard.html")

    def test_invalid_get_view_redirects_when_not_logged_in(self):
        self._assert_require_login(self.url)
