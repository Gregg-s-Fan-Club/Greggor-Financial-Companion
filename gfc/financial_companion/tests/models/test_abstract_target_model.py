from .test_abstract_model_base import AbstractModelTestCase
from django.db.models.base import ModelBase
from decimal import Decimal
from ...helpers import Timespan, TransactionType, CurrencyType
from ...models import AbstractTarget


class AbstractTargetModelTestCase(AbstractModelTestCase):
    """Test file for abstract target model class"""

    fixtures: list[str] = ["example_abstract_targets.json"]

    @classmethod
    def setUpClass(self) -> None:
        """Create temporary model"""
        self.mixin: AbstractTarget = AbstractTarget
        super().setUpClass()

    def setUp(self) -> None:
        super().setUp()
        self.test_model: ModelBase = self.model.objects.get(id=1)

    def test_valid_target(self) -> None:
        self._assert_model_is_valid()

    def test_valid_amount_integer(self) -> None:
        self.test_model.amount: float = 99
        self._assert_model_is_valid()

    def test_valid_accepts_amount_more_than_zero(
            self) -> None:
        self.test_model.amount: Decimal = Decimal('0.01')
        self.test_model.save()
        self._assert_model_is_valid()

    def test_valid_amount_2_decimal_places(self) -> None:
        self.test_model.amount: float = Decimal('99.99')
        self._assert_model_is_valid()

    def test_invalid_rejects_amount_less_than_equal_to_zero(
            self) -> None:
        self.test_model.amount: Decimal = Decimal('0.00')
        self._assert_model_is_invalid()

    def test_invalid_amount_more_than_2_decimal_places(self) -> None:
        self.test_model.amount: float = Decimal('99.999')
        self._assert_model_is_invalid()

    def test_valid_amount_can_be_15_digits_long(self) -> None:
        self.test_model.amount: int = Decimal('1234567890123.45')
        self._assert_model_is_valid()

    def test_invalid_amount_cannnot_be_more_than_15_digits_long(self) -> None:
        self.test_model.amount: int = Decimal('12345678901234.56')
        self._assert_model_is_invalid()

    def test_valid_timespan_enum_options(self) -> None:
        for timespan in Timespan:
            self.test_model.timespan: str = timespan
            self._assert_model_is_valid()

    def test_invalid_timespan_must_be_in_enum(self) -> None:
        self.test_model.timespan: str = "incorrect"
        self._assert_model_is_invalid()

    def test_invalid_timespan_cannot_be_empty(self) -> None:
        self.test_model.timespan: str = ""
        self._assert_model_is_invalid()

    def test_valid_target_type_enum_options(self) -> None:
        for target_type in TransactionType:
            self.test_model.target_type: str = target_type
            self._assert_model_is_valid()

    def test_invalid_target_type_must_be_in_enum(self) -> None:
        self.test_model.target_type: str = "incorrect"
        self._assert_model_is_invalid()

    def test_invalid_target_type_cannot_be_empty(self) -> None:
        self.test_model.target_type: str = ""
        self._assert_model_is_invalid()

    def test_valid_currency_enum_options(self) -> None:
        for currency in CurrencyType:
            self.test_model.currency: str = currency
            self._assert_model_is_valid()

    def test_valid_default_currency_is_gbp(self) -> None:
        no_currency_input_model: ModelBase = self.model.objects.create(
            target_type=TransactionType.INCOME,
            timespan=Timespan.WEEK,
            amount=99,
        )
        self.assertTrue(CurrencyType.GBP == no_currency_input_model.currency)

    def test_invalid_currency_must_be_in_enum(self) -> None:
        self.test_model.currency: str = "inc"
        self._assert_model_is_invalid()

    def test_invalid_currency_cannot_be_empty(self) -> None:
        self.test_model.currency: str = ""
        self._assert_model_is_invalid()

    def test_valid_target_is_complete(self) -> None:
        complete = self.test_model.is_complete()
        self.assertEqual(complete, False)

    def test_get_model_name_function_when_plural_is_false(self) -> None:
        self.assertEquals(self.test_model.get_model_name(), "target")

    def test_get_model_name_function_when_plural_is_true(self) -> None:
        self.assertEquals(
            self.test_model.get_model_name(
                plural=True), "targets")

    def test_get_str_function(self) -> None:
        self.assertEquals(self.test_model.__str__(), "target")
