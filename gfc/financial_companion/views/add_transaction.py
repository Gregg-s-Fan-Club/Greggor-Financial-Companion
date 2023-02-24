from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from financial_companion.forms import AddTransactionForm, AddTransactionsViaBankStatementForm
from financial_companion.models import Transaction, PotAccount, BankAccount, Account, Category, User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from typing import Any


@login_required
def add_transaction_view(request: HttpRequest) -> HttpResponse:
    """View to record a transaction made"""

    user = request.user
    categories = Category.objects.filter(user=user.id)

    if request.method == 'POST':
        form = AddTransactionForm(user, request.POST, request.FILES)
        form.fields['category'].queryset = categories
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AddTransactionForm(user)
        form.fields['category'].queryset = categories
    return render(request, "pages/add_transaction.html",
                  {'form': form, 'edit': False})


@login_required
def edit_transaction_view(request: HttpRequest, pk) -> HttpResponse:
    try:
        transaction = Transaction.objects.get(id=pk)
    except ObjectDoesNotExist:
        return redirect('dashboard')
    else:
        user = request.user
        categories = Category.objects.filter(user=user.id)
        if request.method == 'POST':
            form = AddTransactionForm(
                user, request.POST, request.FILES, instance=transaction)
            form.fields['category'].queryset = categories
            if form.is_valid():
                form.save(instance=transaction)
                return redirect('dashboard')
        form = AddTransactionForm(user, instance=transaction)
        form.fields['category'].queryset = categories
        return render(request, "pages/add_transaction.html",
                      {'form': form, 'edit': True, 'pk': pk})


@login_required
def delete_transaction_view(request: HttpRequest, pk) -> HttpResponse:
    try:
        transaction = Transaction.objects.get(id=pk)
    except ObjectDoesNotExist:
        return redirect('dashboard')
    else:
        transaction.delete()
        messages.add_message(
            request,
            messages.WARNING,
            "The transaction has been deleted")
        return redirect('dashboard')


@login_required
def add_transactions_via_bank_statement(request: HttpRequest) -> HttpResponse:
    user: User = request.user

    if request.method == 'POST':
        form: AddTransactionsViaBankStatementForm = AddTransactionsViaBankStatementForm(
            request.POST, request.FILES, user=user)
        if form.is_valid():
            try:
                transactions: list[Transaction] = form.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"{len(transactions)} new transactions added"
                )
                return redirect('view_transactions_redirect')
            except Exception as e:
                print(e)
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Error scanning document, please ensure it is a valid bank statement"
                )
    else:
        form: AddTransactionsViaBankStatementForm = AddTransactionsViaBankStatementForm(
            user=user)
    return render(request, "pages/transactions_via_bank_statement_form.py.html",
                  {
                      'form': form
                  }
                  )
