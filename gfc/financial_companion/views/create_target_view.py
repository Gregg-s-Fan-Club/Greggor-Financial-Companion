from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from financial_companion.forms import TargetForm, TargetFilterForm
from django.contrib.auth.decorators import login_required
from ..models import Category, CategoryTarget, PotAccount, AccountTarget, UserTarget
from django.contrib import messages
from financial_companion.models import CategoryTarget, Category, UserTarget, AbstractTarget
from financial_companion.helpers import paginate, get_warning_messages_for_targets
from django.db.models import QuerySet
import re
from typing import Any
from django.core.paginator import Page


def create_target(request, Target, current_item) -> HttpResponse:
    """Render base request data for create target views"""
    title_first_word: str = re.split(r"\B([A-Z])", Target.__name__)[0]
    title: str = f'{title_first_word} Target'
    form: TargetForm = TargetForm(
        request.POST,
        foreign_key=current_item,
        form_type=Target)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "Target successfully created")
            return None
    else:
        form: TargetForm = TargetForm(
            foreign_key=current_item, form_type=Target)
    return render(request, "pages/create_targets.html",
                  {'form': form, "form_toggle": True, 'title': title})


@login_required
def create_category_target_view(request: HttpRequest, pk: int) -> HttpResponse:
    """View to allow users to add a target to a category"""
    # check is id valid
    try:
        current_category: Category = Category.objects.get(
            id=pk, user=request.user)
    except Exception:
        return redirect("dashboard")
    to_return: HttpResponse = create_target(
        request,
        CategoryTarget,
        current_category)

    if to_return is None:
        return redirect('individual_category_redirect',
                        pk=current_category.id)
    else:
        return to_return


@login_required
def create_account_target_view(request: HttpRequest, pk: int) -> HttpResponse:
    """View to allow users to add a target to an account"""
    # check is id valid
    try:
        current_account: PotAccount = PotAccount.objects.get(
            id=pk, user=request.user)
    except Exception:
        return redirect("dashboard")

    to_return: HttpResponse = create_target(
        request,
        AccountTarget,
        current_account)

    if to_return is None:
        return redirect('individual_account_redirect',
                        pk=current_account.id)
    else:
        return to_return


@login_required
def create_user_target_view(request: HttpRequest) -> HttpResponse:
    """View to allow users to add a target to a user"""
    to_return: HttpResponse = create_target(request, UserTarget, request.user)

    if to_return is None:
        return redirect('view_targets')
    else:
        return to_return


def edit_target(request: HttpRequest, Target, current_item,
                foreign_key) -> HttpResponse:
    """Render base request data for edit target views"""
    title_first_word: str = re.split(r"\B([A-Z])", Target.__name__)[0]
    title: str = f'{title_first_word} Target'
    if request.method == "POST":
        form: TargetForm = TargetForm(
            request.POST,
            foreign_key=foreign_key,
            instance=current_item,
            form_type=Target)
        if form.is_valid():
            messages.add_message(
                request,
                messages.SUCCESS,
                "This target has been successfully updated")
            form.save()
            return None
    else:
        form: TargetForm = TargetForm(
            foreign_key=foreign_key,
            instance=current_item,
            form_type=Target)
    return render(request, "pages/create_targets.html",
                  {'form': form, "form_toggle": False, 'title': title})


@login_required
def edit_category_target_view(request: HttpRequest, pk: int) -> HttpResponse:
    """View to allow users to edit a category target"""
    # check is id valid
    try:
        current_category_target: CategoryTarget = CategoryTarget.objects.get(
            id=pk)
        if current_category_target.category.user != request.user:
            return redirect("categories_list", search_name="all")
    except Exception:
        return redirect("dashboard")

    to_return: HttpResponse = edit_target(
        request,
        CategoryTarget,
        current_category_target,
        current_category_target.category)

    if to_return is None:
        return redirect('individual_category_redirect',
                        pk=current_category_target.category.id)
    else:
        return to_return


@login_required
def edit_account_target_view(request: HttpRequest, pk: int) -> HttpResponse:
    """View to allow users to edit an account target"""
    # check is id valid
    try:
        current_account_target: AccountTarget = AccountTarget.objects.get(
            id=pk)
        if current_account_target.account.user != request.user:
            return redirect("view_accounts")
    except Exception:
        return redirect("dashboard")
    to_return: HttpResponse = edit_target(
        request,
        AccountTarget,
        current_account_target,
        current_account_target.account)

    if to_return is None:
        return redirect('individual_account_redirect',
                        pk=current_account_target.account.id)
    else:
        return to_return


@login_required
def edit_user_target_view(request: HttpRequest, pk: int) -> HttpResponse:
    """View to allow users to edit a user target"""
    # check is id valid
    try:
        current_user_target: UserTarget = UserTarget.objects.get(
            id=pk)
        if current_user_target.user != request.user:
            return redirect("dashboard")
    except Exception:
        return redirect("dashboard")
    to_return: HttpResponse = edit_target(
        request,
        UserTarget,
        current_user_target,
        request.user)

    if to_return is None:
        return redirect('view_targets')
    else:
        return to_return


@login_required
def delete_category_target_view(request: HttpRequest, pk: int) -> HttpResponse:
    """View to allow users to delete a category target"""
    # check is id valid
    try:
        current_category_target: CategoryTarget = CategoryTarget.objects.get(
            id=pk)
        category_id = current_category_target.category.id
        if current_category_target.category.user != request.user:
            return redirect("categories_list", search_name="all")
    except Exception:
        return redirect("dashboard")
    else:
        current_category_target.delete()
    messages.add_message(
        request,
        messages.WARNING,
        "This category target has been deleted")
    return redirect('individual_category_redirect', pk=category_id)


@login_required
def delete_account_target_view(request: HttpRequest, pk: int) -> HttpResponse:
    """View to allow users to delete an account target"""
    # check is id valid
    try:
        current_account_target: AccountTarget = AccountTarget.objects.get(
            id=pk)
        account_id: int = current_account_target.account.id
        if current_account_target.account.user != request.user:
            return redirect("view_accounts")
    except Exception:
        return redirect("dashboard")
    else:
        current_account_target.delete()
    messages.add_message(
        request,
        messages.WARNING,
        "This account target has been deleted")
    return redirect('individual_account_redirect',
                    pk=account_id)


@login_required
def delete_user_target_view(request: HttpRequest, pk: int) -> HttpResponse:
    """View to allow users to delete an user target"""
    # check is id valid
    try:
        current_user_target: UserTarget = UserTarget.objects.get(
            id=pk, user=request.user)
    except Exception:
        return redirect("dashboard")
    else:
        current_user_target.delete()
    messages.add_message(
        request,
        messages.WARNING,
        "This user target has been deleted")
    return redirect("dashboard")


@login_required
def view_targets(request: HttpRequest, time: str = "all",
                 income_or_expense: str = "all", target_type: str = "all") -> HttpResponse:
    """View to allow users to view all their targets"""
    if request.method == "POST":
        form: TargetFilterForm = TargetFilterForm(request.POST)
        if form.is_valid():
            form_output: dict[str, str] = {
                "time": form.get_time(),
                "income_or_expense": form.get_income_or_expense(),
                "target_type": form.get_target_type()
            }
            if len({k: v for k, v in form_output.items() if v}) == 0:
                return redirect("view_targets")

            for key in form_output:
                if form_output[key] == "":
                    form_output[key]: str = "all"
            return redirect("view_targets", **form_output)
    else:
        form: TargetFilterForm = TargetFilterForm()

    targets: list[AbstractTarget] = [target for target in request.user.get_all_targets() if (
        (time == target.timespan or time == "all") and
        (target_type == target.get_model_name() or target_type == "all") and
        (income_or_expense == target.target_type or income_or_expense == "all")
    )]

    list_of_targets: Page = paginate(request.GET.get('page', 1), targets)

    targets_for_messages: QuerySet[UserTarget] = UserTarget.objects.filter(
        user=request.user)
    request = get_warning_messages_for_targets(
        request, False, targets_for_messages)

    return render(request, "pages/view_targets.html",
                  {'targets': list_of_targets, 'form': form})
