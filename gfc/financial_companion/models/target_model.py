from django.db.models import (
    Model,
    CharField,
    DecimalField,
    ForeignKey,
    CASCADE
)

from django.core.validators import MinValueValidator
from .category_model import Category
from .user_model import User
from .accounts_model import PotAccount
from ..helpers import Timespan, TransactionType, CurrencyType
from decimal import Decimal
from financial_companion.templatetags import get_completeness


class AbstractTarget(Model):
    """Abstract model for target spending and saving"""

    target_type: CharField = CharField(
        choices=TransactionType.choices, max_length=7
    )

    timespan: CharField = CharField(
        choices=Timespan.choices, max_length=5
    )

    amount: DecimalField = DecimalField(
        decimal_places=2, max_digits=15, validators=[MinValueValidator(Decimal('0.01'))]
    )

    currency: CharField = CharField(
        choices=CurrencyType.choices, max_length=5, default=CurrencyType.GBP
    )

    class Meta:
        abstract: bool = True

    def is_complete(self) -> bool:
        """Returns boolean if the target is complete or not"""
        if get_completeness(self) >= 100:
            return True
        else:
            return False

    def is_nearly_complete(self) -> bool:
        """Returns boolean if the target if between 70% and 100% completeness"""
        completeness: float = get_completeness(self)
        if completeness >= 75 and completeness < 100:
            return True
        else:
            return False

    def get_model_name(self, plural: bool = False) -> str:
        """Get model name with pluralisation if necessary"""
        if plural:
            return "targets"
        else:
            return "target"

    def __str__(self) -> str:
        return self.get_model_name()


class CategoryTarget(AbstractTarget):
    """Model for target spending and saving on categories"""

    category: ForeignKey = ForeignKey(Category, on_delete=CASCADE)

    class Meta:
        unique_together: list[str] = ["target_type", "timespan", "category"]

    def get_model_name(self, plural: bool = False) -> str:
        """Get model name with pluralisation if necessary"""
        if plural:
            return "categories"
        else:
            return "category"

    def __str__(self) -> str:
        return self.category.name


class UserTarget(AbstractTarget):
    """Model for target spending and saving of users"""

    user: ForeignKey = ForeignKey(User, on_delete=CASCADE)

    class Meta:
        unique_together: list[str] = ["target_type", "timespan", "user"]

    def get_model_name(self, plural: bool = False) -> str:
        """Get model name with pluralisation if necessary"""
        if plural:
            return "users"
        else:
            return "user"

    def __str__(self) -> str:
        return "personal target"


class AccountTarget(AbstractTarget):
    """Model for target spending and saving of users"""

    account: ForeignKey = ForeignKey(PotAccount, on_delete=CASCADE)

    class Meta:
        unique_together: list[str] = ["target_type", "timespan", "account"]

    def get_model_name(self, plural: bool = False) -> str:
        """Get model name with pluralisation if necessary"""
        if plural:
            return "accounts"
        else:
            return "account"

    def __str__(self) -> str:
        return self.account.name
