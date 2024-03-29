from .test_abstract_model_base import AbstractModelTestCase
from django.db.models.base import ModelBase
from decimal import Decimal

from ...helpers import CurrencyType
from ...models import AbstractTransaction, Account, PotAccount, User


class AbstractTransactionModelTestCase(AbstractModelTestCase):
    """Test file for abstract transaction model class"""

    fixtures: list[str] = [
        "example_abstract_transactions.json",
        "example_category.json",
        "example_accounts.json",
        "example_users.json"]

    @classmethod
    def setUpClass(self):
        """Create temporary model"""
        self.mixin: AbstractTransaction = AbstractTransaction
        super().setUpClass()

    def setUp(self) -> None:
        super().setUp()
        self.test_model: ModelBase = self.model.objects.get(id=1)

    def test_valid_transaction(self):
        self._assert_model_is_valid()

    def test_valid_title(self):
        self.test_model.title: str = "Test transaction title"
        self._assert_model_is_valid()

    def test_title_may_not_be_blank(self):
        self.test_model.title: str = ""
        self._assert_model_is_invalid()

    def test_valid_title_of_30_characters(self):
        self.test_model.title: float = "x" * 30
        self._assert_model_is_valid()

    def test_invalid_title_of_more_than_30_characters(self):
        self.test_model.title: float = "x" * 31
        self._assert_model_is_invalid()

    def test_valid_description(self):
        self.test_model.description: str = "Test transaction description"
        self._assert_model_is_valid()

    def test_title_may_be_blank(self):
        self.test_model.description: str = ""
        self._assert_model_is_valid()

    def test_valid_description_of_200_characters(self):
        self.test_model.description: float = "x" * 200
        self._assert_model_is_valid()

    def test_invalid_description_of_more_than_200_characters(self):
        self.test_model.description: float = "x" * 201
        self._assert_model_is_invalid()

    def test_file_may_be_blank(self):
        self.test_model.file = ''
        self._assert_model_is_valid()

    def test_valid_amount_integer(self):
        self.test_model.amount: float = 99
        self._assert_model_is_valid()

    def test_valid_amount_2_decimal_places(self):
        self.test_model.amount: float = Decimal('99.99')
        self._assert_model_is_valid()

    def test_invalid_amount_more_than_2_decimal_places(self):
        self.test_model.amount: float = Decimal('99.999')
        self._assert_model_is_invalid()

    def test_amount_may_not_be_blank(self):
        self.test_model.amount: float = None
        self._assert_model_is_invalid()

    def test_valid_currency_type_enum_options(self):
        for currency_type in CurrencyType:
            self.test_model.currency: str = currency_type
            self._assert_model_is_valid()

    def test_invalid_currency_type_must_be_in_enum(self):
        self.test_model.currency: str = "incorrect"
        self._assert_model_is_invalid()

    def test_invalid_currency_type_may_not_be_blank(self):
        self.test_model.currency: str = ""
        self._assert_model_is_invalid()

    def test_amount_is_valid_for_values_greater_than_0_01(self):
        self.test_model.amount: Decimal = Decimal("0.01")
        self._assert_model_is_valid()

    def test_amount_is_invalid_for_values_less_than_0_01(self):
        self.test_model.amount: Decimal = Decimal("0.00")
        self._assert_model_is_invalid()

    def test_transaction_cannot_have_regular_account_for_sender_and_receiver(
            self):
        user: User = User.objects.get(id=1)
        test_sender_account: Account = Account.objects.create(
            name="Test sender", description="this is a test account", user=user)
        test_receiver_account: Account = Account.objects.create(
            name="Test receiver", description="this is a test account", user=user)
        self.test_model.sender_account: Account = test_sender_account
        self.test_model.receiver_account: Account = test_receiver_account
        self._assert_model_is_invalid()

    def test_transaction_can_have_regular_account_for_sender_or_receiver(self):
        user: User = User.objects.get(id=1)
        test_account1: PotAccount = PotAccount.objects.create(
            name="Test sender",
            description="this is a test account",
            user=user,
            balance=10000,
            currency="GBP")
        test_account2: Account = Account.objects.create(
            name="Test receiver", description="this is a test account", user=user)
        self.test_model.sender_account: Account = test_account1
        self.test_model.receiver_account: Account = test_account2
        self._assert_model_is_valid()
        self.test_model.sender_account: Account = test_account2
        self.test_model.receiver_account: Account = test_account1
        self._assert_model_is_valid()
