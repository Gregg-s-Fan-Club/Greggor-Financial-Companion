from django import forms
from django.core.validators import FileExtensionValidator
from financial_companion.models import Transaction, Account, Category, PotAccount
from financial_companion.helpers import ParseStatementPDF, CurrencyType
from datetime import datetime
from django.utils.timezone import make_aware
from typing import Any

class AddTransactionForm(forms.ModelForm):
    """Form to add a new transaction"""

    class Meta:
        model = Transaction
        fields = [
            'title',
            'description',
            'image',
            'category',
            'amount',
            'currency',
            'sender_account',
            'receiver_account']

    def save(self, instance: Transaction = None) -> Transaction:
        """Create a new transaction."""
        super().save(commit=False)
        if instance is None:
            transaction = Transaction.objects.create(
                title=self.cleaned_data.get('title'),
                description=self.cleaned_data.get('description'),
                image=self.cleaned_data.get('image'),
                category=self.cleaned_data.get('category'),
                amount=self.cleaned_data.get('amount'),
                currency=self.cleaned_data.get('currency'),
                sender_account=self.cleaned_data.get('sender_account'),
                receiver_account=self.cleaned_data.get('receiver_account')
            )
        else:
            transaction: Transaction = instance
            transaction.title = self.cleaned_data.get('title')
            transaction.description = self.cleaned_data.get('description')
            transaction.image = self.cleaned_data.get('image')
            transaction.category = self.cleaned_data.get('category')
            transaction.amount = self.cleaned_data.get('amount')
            transaction.currency = self.cleaned_data.get('currency')
            transaction.sender_account = self.cleaned_data.get(
                'sender_account')
            transaction.receiver_account = self.cleaned_data.get(
                'receiver_account')
            transaction.save()
        return transaction

class AddTransactionsViaBankStatementForm(forms.Form):
    """Form to upload bank statement to add new transactions"""
    bank_statement: forms.FileField = forms.FileField(
        validators=[FileExtensionValidator(['pdf'])]
    )
    account_currency: forms.ChoiceField = forms.ChoiceField(
        choices=CurrencyType.choices
    )

    def __init__(self, *args, **kwargs):
        user=kwargs.pop("user", None)
        super(AddTransactionsViaBankStatementForm, self).__init__(*args, **kwargs)

        self.fields['account']: forms.ModelChoiceField = forms.ModelChoiceField(
            queryset = PotAccount.objects.filter(user=user)
        )

    def save(self):
        super().full_clean()

        bank_statement: forms.FileInput = self.cleaned_data["bank_statement"]
        account: Account = self.cleaned_data["account"]
        currency: CurrencyType = self.cleaned_data["account_currency"]

        bank_statement_file_path: str = bank_statement.temporary_file_path()
        bank_statement_parser: ParseStatementPDF = ParseStatementPDF()
        parsed_transactions_list: list[dict[str, Any]] = bank_statement_parser.get_transactions_from_pdf_statement(bank_statement_file_path)
        transactions: list[Transaction] = []
        for parsed_transaction in parsed_transactions_list:
            title: str = " ".join(parsed_transaction["description"])
            description: str = "Generate via bank statement"
            date: datetime = make_aware(parsed_transaction["date"])

            transaction_exists_query: dict[str, Any] = {
                "title": title,
                "description": description,
                "amount": parsed_transaction["amount"],
                "currency": currency,
                "time_of_transaction": date
            }
            if len(Transaction.objects.filter(**transaction_exists_query)):
                continue
            
            new_transaction: Transaction = Transaction()
            new_transaction.receiver_account, new_transaction.sender_account = bank_statement_parser.get_sender_receiver(parsed_transaction, account)
            new_transaction.title: str = title
            new_transaction.description: str = description
            new_transaction.amount: float = parsed_transaction["amount"]
            new_transaction.currency: str = currency
            new_transaction.save()
            new_transaction.time_of_transaction: datetime = date
            new_transaction.save()

            transactions = [*transactions, new_transaction]
        return transactions