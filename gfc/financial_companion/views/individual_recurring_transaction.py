from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from ..models import RecurringTransaction, User
from financial_companion.helpers import paginate
from django.core.paginator import Page


@login_required
def individual_recurring_transaction_view(
        request: HttpRequest, pk: int) -> HttpResponse:
    """View to see information on individual recurring transactions"""
    try:
        transaction: RecurringTransaction = RecurringTransaction.objects.get(
            id=pk)
        user: User = request.user
        if (transaction.receiver_account.user !=
                user and transaction.sender_account.user != user):
            return redirect("dashboard")
    except RecurringTransaction.DoesNotExist:
        return redirect("dashboard")
    else:
        transactions_list: Page = paginate(request.GET.get(
            'page', 1), transaction.transactions.all(), 9)
        return render(request, "pages/individual_recurring_transaction.html",
                      {"transaction": transaction, "transactions_list": transactions_list})
