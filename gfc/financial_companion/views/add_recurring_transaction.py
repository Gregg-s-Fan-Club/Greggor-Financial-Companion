from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from financial_companion.forms import AddRecurringTransactionForm
from financial_companion.models import Category, User, RecurringTransaction
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db.models import QuerySet


@login_required
def add_recurring_transaction_view(request: HttpRequest) -> HttpResponse:
    """View to record a recurring transaction"""

    user: User = request.user
    categories: QuerySet[Category] = Category.objects.filter(user=user.id)

    if request.method == 'POST':
        form: AddRecurringTransactionForm = AddRecurringTransactionForm(
            user, request.POST, request.FILES)
        form.fields['category'].queryset: QuerySet[Category] = categories
        if form.is_valid():
            form.save()
            messages.add_message(
                request,
                messages.WARNING,
                "New recurring transaction has been added.")
            return redirect('view_recurring_transactions')
    else:
        form: AddRecurringTransactionForm = AddRecurringTransactionForm(user)
        form.fields['category'].queryset: QuerySet[Category] = categories
    return render(request, "pages/add_recurring_transaction.html",
                  {'form': form, 'edit': False})


@login_required
def edit_recurring_transaction_view(
        request: HttpRequest, pk: int) -> HttpResponse:
    """View to edit a recurring transaction"""
    try:
        transaction: RecurringTransaction = RecurringTransaction.objects.get(
            id=pk)
        user: User = request.user
        if (transaction.receiver_account.user !=
                user and transaction.sender_account.user != user):
            return redirect('view_recurring_transactions')
    except ObjectDoesNotExist:
        return redirect('view_recurring_transactions')
    else:
        user: User = request.user
        categories: QuerySet[Category] = Category.objects.filter(user=user.id)
        if request.method == 'POST':
            form: AddRecurringTransactionForm = AddRecurringTransactionForm(
                user, request.POST, request.FILES, instance=transaction)
            form.fields['category'].queryset: QuerySet[Category] = categories
            if form.is_valid():
                form.save(instance=transaction)
                messages.add_message(
                    request,
                    messages.WARNING,
                    "The recurring transaction has been updated")
                return redirect('individual_recurring_transaction', pk=pk)
        else:
            form: AddRecurringTransactionForm = AddRecurringTransactionForm(
                user, instance=transaction)
        form.fields['category'].queryset: QuerySet[Category] = categories
        return render(request, "pages/add_recurring_transaction.html",
                      {'form': form, 'edit': True, 'pk': pk})


@login_required
def delete_recurring_transaction_view(
        request: HttpRequest, pk) -> HttpResponse:
    """View to delete a recurring transaction"""
    try:
        transaction: RecurringTransaction = RecurringTransaction.objects.get(
            id=pk)
    except ObjectDoesNotExist:
        return redirect('dashboard')
    else:
        transaction.delete()
        messages.add_message(
            request,
            messages.WARNING,
            "The recurring transaction has been deleted")
        return redirect('view_recurring_transactions')
