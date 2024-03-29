from .test_model_base import ModelTestCase
from ...helpers import Timespan
from ...models import RecurringTransaction, Transaction


class RecurringTransactionTestCase(ModelTestCase):
    """Test file for RecurringTransaction model class"""

    def setUp(self) -> None:
        super().setUp()
        self.test_model: RecurringTransaction = RecurringTransaction.objects.get(
            id=2)

    def test_valid_recurring_transaction(self):
        self._assert_model_is_valid()

    def test_valid_transaction_start_Date(self):
        self.test_model.start_date: str = "2023-01-31"
        self._assert_model_is_valid()

    def test_start_date_cannot_be_blank(self):
        self.test_model.start_date: str = ""
        self._assert_model_is_invalid()

    def test_end_date_cannot_be_blank(self):
        self.test_model.end_date: str = ""
        self._assert_model_is_invalid()

    def test_interval_valid(self):
        self.test_model.interval: Timespan = Timespan.MONTH
        self._assert_model_is_valid()

    def test_valid_add_transaction(self):
        transaction: Transaction = Transaction.objects.all().first()
        self.assertEqual(0, len(self.test_model.transactions.all()))
        self.test_model.add_transaction(transaction)
        self.assertEqual(1, len(self.test_model.transactions.all()))

    def test_valid_add_transaction_does_not_add_same_transaction_twice(self):
        transaction: Transaction = Transaction.objects.all().first()
        self.assertEqual(0, len(self.test_model.transactions.all()))
        self.test_model.add_transaction(transaction)
        self.test_model.add_transaction(transaction)
        self.assertEqual(1, len(self.test_model.transactions.all()))
