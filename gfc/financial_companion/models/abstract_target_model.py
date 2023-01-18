from django.db.models import (
    Model,
    CharField,
    DecimalField
)


from ..helpers.enums import Timespan, TransactionType

class AbstractTarget(Model):
    """Abstract model for target spending and saving"""

    transaction_type: CharField = CharField(
        choices=TransactionType.choices, max_length=7
    )

    timespan: CharField = CharField(
        choices=Timespan.choices, max_length=5
    )

    amount: DecimalField = DecimalField(
        decimal_places=2, max_digits=None
    )

    class Meta:
        abstract = True

