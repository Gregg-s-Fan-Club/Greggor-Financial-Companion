from django import forms
from financial_companion.models import RecurringTransaction


class RecurringTransactionForm(forms.ModelForm):
    """Form to log recurring transactions"""

    class Meta:
        model: RecurringTransaction = RecurringTransaction
        fields: list[str] = [
            'title',
            'file',
            'category',
            'amount',
            'currency',
            'sender_account',
            'reciever_account',
            'start_date',
            'interval',
            'end_date']
        widgets: dict[str, forms.Textarea] = {'description': forms.Textarea()}

    def clean(self):
        """Generate messages for any errors"""
        super.clean()

        if self.end_date is not None and self.start_date is not None:
            if self.end_date < self.start_date:
                self.add_error("End date must be after start date.")

    def save(self, instance: RecurringTransaction = None) -> RecurringTransaction:
        """Record the inputted transaction"""
        super.save()
