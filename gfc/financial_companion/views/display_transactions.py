from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from ..models import Transaction, User
from financial_companion.helpers import TransactionType
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from financial_companion.helpers import paginate


@login_required
def view_users_transactions(request: HttpRequest,
                            filter_type: str) -> HttpResponse:
    user: User = request.user

    if not (filter_type in TransactionType.get_send_list()
            or filter_type in TransactionType.get_received_list()):
        return redirect('dashboard')

    transactions: list[Transaction] = sorted(list(dict.fromkeys(user.get_user_transactions(filter_type))), key=lambda x: x.time_of_transaction, reverse=True)

    list_of_transactions = paginate(request.GET.get('page', 1), transactions)

    return render(request, "pages/display_transactions.html",
                  {'transactions': list_of_transactions})


@login_required
def view_users_transactions_redirect(request: HttpRequest) -> HttpResponse:
    return redirect('view_transactions', filter_type="all")


@login_required
def filter_transaction_request(request, redirect_name: str):
    if 'sent' in request.POST:
        return redirect(reverse(redirect_name, kwargs={'filter_type': "sent"}))
    elif 'received' in request.POST:
        return redirect(reverse(redirect_name, kwargs={
                        'filter_type': "received"}))
    elif 'all' in request.POST:
        return redirect(reverse(redirect_name, kwargs={'filter_type': "all"}))
    else:
        return redirect('dashboard')


@login_required
def filter_transaction_request_with_pk(request, redirect_name: str, pk: int):
    if 'sent' in request.POST:
        return redirect(reverse(redirect_name, kwargs={
                        'pk': pk, 'filter_type': "sent"}))
    elif 'received' in request.POST:
        return redirect(reverse(redirect_name, kwargs={
                        'pk': pk, 'filter_type': "received"}))
    elif 'all' in request.POST:
        return redirect(reverse(redirect_name, kwargs={
                        'pk': pk, 'filter_type': "all"}))
    else:
        return redirect('dashboard')
