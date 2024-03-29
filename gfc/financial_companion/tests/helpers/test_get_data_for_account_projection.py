from .test_helper_base import HelperTestCase
from financial_companion.helpers import get_data_for_account_projection
from typing import Any


class GetDataForAccountProjectionHelperFunctionTestCase(HelperTestCase):
    """Test file for the get_data_for_account_projection helpers function"""

    def setUp(self):
        super().setUp()
        self.valid_user_with_savings_accounts: int = 1
        self.valid_user_without_savings_accounts: int = 2
        self.invalid_user: int = -1

    def test_return_context_valid_user_with_savings_accounts(self):
        self.context: dict[str, Any] = get_data_for_account_projection(
            self.valid_user_with_savings_accounts)
        self._assert_context_is_valid()
        self._assert_bank_accounts_is_(True)
        self._assert_bank_accounts_info_is_(True)

    def test_return_context_valid_user_without_savings_accounts(self):
        self.context: dict[str, Any] = get_data_for_account_projection(
            self.valid_user_without_savings_accounts)
        self._assert_context_is_valid()
        self._assert_bank_accounts_is_(False)
        self._assert_bank_accounts_info_is_(False)

    def test_return_context_invalid_user(self):
        self.context: dict[str, Any] = get_data_for_account_projection(
            self.invalid_user)
        self._assert_context_is_valid()
        self._assert_bank_accounts_is_(False)
        self._assert_bank_accounts_info_is_(False)

    def _assert_context_is_valid(self):
        """Assert required data is in context"""
        context: dict[str, Any] = self.context

        self.assertTrue('bank_accounts' in context)
        self.assertTrue('bank_account_infos' in context)
        self.assertTrue('timescale_dict' in context)
        self.assertTrue('timescales_strings' in context)
        self.assertTrue('conversion_to_main_currency_JSON' in context)
        self.assertTrue('conversion_to_main_currency' in context)
        self.assertTrue('main_currency' in context)

        timescale_dict: dict[int, str] = context['timescale_dict']
        timescales_strings: list[str] = context['timescales_strings']
        conversion_to_main_currency_JSON: str = context['conversion_to_main_currency_JSON']
        conversion_to_main_currency: dict[str,
                                          Any] = context['conversion_to_main_currency']
        main_currency: str = context['main_currency']

        self.assertNotEqual(len(timescale_dict), 0)
        self.assertNotEqual(len(timescales_strings), 0)
        self.assertNotEqual(len(conversion_to_main_currency_JSON), 0)
        self.assertNotEqual(len(conversion_to_main_currency), 0)
        self.assertEqual(len(main_currency), 3)

        self.assertIsInstance(timescale_dict, dict)
        self.assertIsInstance(timescales_strings, list)
        self.assertIsInstance(conversion_to_main_currency_JSON, str)
        self.assertIsInstance(conversion_to_main_currency, dict)
        self.assertIsInstance(main_currency, str)

    def _assert_bank_accounts_is_(self, validity: bool):
        """Assert bank accounts in context is valid"""
        bank_accounts: dict[str, Any] = self.context['bank_accounts']
        self.assertTrue((len(bank_accounts) != 0) == validity)
        self.assertIsInstance(bank_accounts, dict)

    def _assert_bank_accounts_info_is_(self, validity: int):
        """Assert bank account info in context is valid"""
        bank_account_infos: str = self.context['bank_account_infos']
        self.assertTrue((len(bank_account_infos) != 2) == validity)
        self.assertIsInstance(bank_account_infos, str)
