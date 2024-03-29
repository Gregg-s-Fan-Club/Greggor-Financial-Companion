from django import forms
from django.core.validators import FileExtensionValidator
from financial_companion.models import Transaction, Account, Category, PotAccount, User
from financial_companion.helpers import ParseStatementPDF, CurrencyType
from datetime import datetime
from django.utils.timezone import make_aware
from typing import Any
from decimal import Decimal
from django.db.models import QuerySet


class AddTransactionForm(forms.ModelForm):
    """Form to add a new transaction"""

    def __init__(self, user, *args, **kwargs):
        super(AddTransactionForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset: QuerySet[Category] = Category.objects.filter(
            user=user.id)
        self.fields['sender_account'].queryset: QuerySet[Account] = Account.objects.filter(
            user=user.id)
        self.fields['receiver_account'].queryset: QuerySet[Account] = Account.objects.filter(
            user=user.id)
        self.fields['category'].label_from_instance: str = self.label_from_instance
        self.fields['sender_account'].label_from_instance: str = self.label_from_instance
        self.fields['receiver_account'].label_from_instance: str = self.label_from_instance
        self.user: User = user

    def label_from_instance(self, obj) -> str:
        """Return objects name"""
        return obj.name

    class Meta:
        model: Transaction = Transaction
        fields: list[str] = [
            'title',
            'description',
            'file',
            'category',
            'amount',
            'currency',
            'sender_account',
            'receiver_account']

    def save(self, instance: Transaction = None) -> Transaction:
        """Create a new transaction."""
        super().save(commit=False)
        if instance is None:
            transaction: Transaction = Transaction.objects.create(
                title=self.cleaned_data.get('title'),
                description=self.cleaned_data.get('description'),
                file=self.cleaned_data.get('file'),
                category=self.cleaned_data.get('category'),
                amount=self.cleaned_data.get('amount'),
                currency=self.cleaned_data.get('currency'),
                sender_account=self.cleaned_data.get('sender_account'),
                receiver_account=self.cleaned_data.get('receiver_account')
            )
        else:
            transaction: Transaction = super().save(commit=True)

        return transaction

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        sender_account: Account = self.cleaned_data.get('sender_account')
        receiver_account: Account = self.cleaned_data.get('receiver_account')
        users_accounts: QuerySet[PotAccount] = PotAccount.objects.filter(
            user=self.user)
        ids: list[int] = []
        for account in users_accounts:
            ids.append(account.id)
        if sender_account == receiver_account:
            self.add_error(
                'receiver_account',
                'The sender and receiver accounts cannot be the same.')
        elif not ((sender_account.id in ids) or (receiver_account.id in ids)):
            self.add_error(
                'sender_account',
                'Neither the sender or reciever are accounts with a balance to track.')
            self.add_error(
                'receiver_account',
                'Neither the sender or reciever are accounts with a balance to track.')


class AddTransactionsViaBankStatementForm(forms.Form):
    """Form to upload bank statement to add new transactions"""
    bank_statement: forms.FileField = forms.FileField(
        validators=[FileExtensionValidator(['pdf'])],
        label="Bank Statement PDF"
    )
    account_currency: forms.ChoiceField = forms.ChoiceField(
        choices=CurrencyType.choices,
        label="Account Currency"
    )
    update_balance: forms.ChoiceField = forms.ChoiceField(
        label="Update Account Balance (Select if you want to set the balance of this account to the close balance on the statement provided)",
        choices=(
            (False, "No"),
            (True, "Yes")
        )
    )

    def __init__(self, *args, **kwargs) -> None:
        self.user: User = kwargs.pop("user", None)
        super(
            AddTransactionsViaBankStatementForm,
            self).__init__(
            *args,
            **kwargs)

        self.fields['account']: forms.ModelChoiceField = forms.ModelChoiceField(
            queryset=PotAccount.objects.filter(user=self.user)
        )

    def save(self) -> Transaction:
        """Create a new transaction via bank statement."""
        super().full_clean()

        bank_statement: forms.FileInput = self.cleaned_data["bank_statement"]
        account: PotAccount = self.cleaned_data["account"]
        currency: CurrencyType = self.cleaned_data["account_currency"]
        update_balance: bool = self.cleaned_data["update_balance"]

        bank_statement_file_path: str = bank_statement.temporary_file_path()
        bank_statement_parser: ParseStatementPDF = ParseStatementPDF()
        parsed_transactions_list: list[dict[str, Any]] = bank_statement_parser.get_transactions_from_pdf_statement(
            bank_statement_file_path)
        transactions: list[Transaction] = []
        for parsed_transaction in parsed_transactions_list:
            title: str = " ".join(parsed_transaction["description"])
            description: str = "Generated via bank statement"
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
            new_transaction.receiver_account, new_transaction.sender_account = bank_statement_parser.get_sender_receiver(
                parsed_transaction, account, self.user)
            new_transaction.title: str = title
            new_transaction.description: str = description
            new_transaction.amount: float = parsed_transaction["amount"]
            new_transaction.currency: str = currency
            new_transaction.save()
            new_transaction.time_of_transaction: datetime = date
            new_transaction.save()

            transactions = [*transactions, new_transaction]

        if update_balance == "True" and len(parsed_transactions_list) > 0:
            account.balance: Decimal = parsed_transactions_list[-1]["balance"]
            account.save()
        return transactions
