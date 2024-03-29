from .test_helper_base import HelperTestCase
from financial_companion.helpers import get_projections_balances, get_projection_timescale_options
from financial_companion.models import BankAccount
from django.db.models import QuerySet
from typing import Any


class GetProjectionBalancesHelperFunctionTestCase(HelperTestCase):
    """Test file for the get_projections_balances helpers function"""

    def setUp(self):
        super().setUp()
        self.bank_accounts: QuerySet[BankAccount] = BankAccount.objects.filter(
            interest_rate__gt=0)
        self.timescales: int = max(get_projection_timescale_options().keys())

    def test_valid_accounts_no_timescale(self):
        self._get_and_test_balances()
        self._assert_projection_valid()

    def test_valid_accounts_valid_timescale(self):
        self.timescales: int = 10
        self._get_and_test_balances()
        self._assert_projection_valid()

    def test_valid_accounts_negative_timescale(self):
        self.timescales: int = -1
        self._get_and_test_balances()
        self._assert_projection_valid()

    def test_no_accounts_no_timescale(self):
        self._get_no_accounts()
        self._get_and_test_balances()
        self._assert_projection_empty()

    def test_no_accounts_valid_timescale(self):
        self.timescales: int = 10
        self._get_no_accounts()
        self._get_and_test_balances()
        self._assert_projection_empty()

    def test_no_accounts_negative_timescale(self):
        self.timescales: int = -1
        self._get_no_accounts()
        self._get_and_test_balances()
        self._assert_projection_empty()

    def _get_no_accounts(self):
        """Set balances to where id is like 0"""
        self.bank_accounts: QuerySet[BankAccount] = BankAccount.objects.filter(
            id__lt=0)

    def _get_and_test_balances(self):
        """Set balances to get projections balances"""
        self.balances: dict[str, list[float]] = get_projections_balances(
            self.bank_accounts, self.timescales)

    def _assert_projection_valid(self):
        """Assert there is the necessary data to display"""
        if self.timescales < 0:
            self.timescales: int = 0

        self.assertEqual(len([*self.balances]), len([*self.bank_accounts]))
        projection: dict[str, Any] = self.balances[[*self.balances.keys()][0]]

        self.assertIsInstance(projection['name'], str)
        self.assertIsInstance(projection['currency'], str)
        self.assertIsInstance(projection['interest_rate'], float)
        self.assertIsInstance(projection['balances'], list)
        self.assertEqual(len(projection['balances']), self.timescales)

    def _assert_projection_empty(self):
        """Assert there is no data to display"""
        self.assertEqual(len([*self.balances]), 0)
