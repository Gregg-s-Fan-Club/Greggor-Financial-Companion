from django import forms
from ..helpers import Timespan, TransactionType, TargetType


class TargetFilterForm(forms.Form):
    """Form to filter targets by time, type or income vs expense"""
    time: forms.ChoiceField = forms.ChoiceField(
        choices=[
            ('',
             '-----')] +
        Timespan.choices,
        required=False)
    income_or_expense: forms.ChoiceField = forms.ChoiceField(
        choices=[('', '-----')] + TransactionType.choices, required=False)
    target_type: forms.ChoiceField = forms.ChoiceField(
        choices=[('', '-----')] + TargetType.choices, required=False)

    def get_time(self) -> Timespan:
        """Get time input from form"""
        self.full_clean()
        return self.cleaned_data["time"]

    def get_income_or_expense(self) -> TransactionType:
        """Get transaction type input from form"""
        self.full_clean()
        return self.cleaned_data["income_or_expense"]

    def get_target_type(self) -> TargetType:
        """Get target type input from form"""
        self.full_clean()
        return self.cleaned_data["target_type"]
