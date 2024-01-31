from typing import Any
from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositForm, WithdrawForm, LoanRequestForm
from django.contrib import messages
from django.http import HttpResponse

# Create your views here.

# we will inherit this view for all transaction such as deposit, withdrawal, transfer, loan request, etc.


class CreateTransactionView(LoginRequiredMixin, CreateView):
    template_name = ''
    model = Transaction
    title = ''
    success_url = reverse_lazy('')

    # passing the account object to the form. get_form_kwargs method is often used to pass additional parameters to a form when it is instantiated. This can be useful for dynamically customizing the behavior of a form based on the context of the view.
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs['account'] = self.request.user.account
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['title'] = self.title
        context.update({
            'title': self.title
        })
        return context


class DepositMoney(CreateTransactionView):
    form_class = DepositForm
    title = 'Deposit Money'

    def get_initial(self):
        initial = {'transaction_type': 'Deposit'}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(
            update_fields=['balance']
        )

        messages.success(
            self.request, f'You have successfully deposited ${amount}')

        return super().form_valid(form)


class WithdrawMoney(CreateTransactionView):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': 'Withdraw'}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount
        account.save(
            update_fields=['balance']
        )

        messages.success(
            self.request, f'You have successfully withdrawn ${amount}')

        return super().form_valid(form)


class LoanRequest(CreateTransactionView):
    form_class = LoanRequestForm
    title = 'Loan Request'

    def get_initial(self):
        initial = {'transaction_type': 'Loan'}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        loan_request_count = Transaction.objects.filter(
            account=self.request.user.account, transaction_type='Loan Request').count()
        loan_approved_count = Transaction.objects.filter(
            account=self.request.user.account, transaction_type='Loan').count()

        if loan_request_count > 0:
            return HttpResponse('You already have a loan request')
        if loan_approved_count >= 3:
            return HttpResponse('You have reached the maximum limit of loan request')

        messages.success(
            self.request, f'You have successfully requested ${amount} loan and awaiting for admin approval')

        return super().form_valid(form)
