from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from financial_companion.forms import AddTransactionForm
from ..models import Transaction
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

@login_required
def add_transaction_view(request: HttpRequest) -> HttpResponse:
    """View to record a transaction made"""

    if request.method == 'POST':
        form = AddTransactionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AddTransactionForm()
    return render(request, "pages/add_transaction.html", {'form': form, 'edit': False})

@login_required
def edit_transaction_view(request: HttpRequest, pk) -> HttpResponse:
    try:
        transaction = Transaction.objects.get(id=pk)
    except ObjectDoesNotExist:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            form = AddTransactionForm(request.POST, request.FILES, instance=transaction)
            if form.is_valid():
                form.save(instance=transaction)
                return redirect('dashboard')
        else:
            form = AddTransactionForm(instance=transaction)
        return render(request, "pages/add_transaction.html", {'form': form, 'edit': True, 'pk':pk})
