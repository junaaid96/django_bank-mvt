from django.views.generic import CreateView, ListView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositForm, WithdrawForm, LoanRequestForm
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect

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


class TransactionReport(LoginRequiredMixin, ListView):
    template_name = ''
    model = Transaction
    balance = 0

    def get_queryset(self):
        # by default all transactions will be shown
        queryset = super().get_queryset().filter(
            account=self.request.user.account)

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date and end_date:
            # converting string to date
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            # transactions will be filtered based on the date range
            # queryset = queryset.filter(
            #     transaction_date__date__range=[start_date, end_date])
            queryset = queryset.filter(
                transaction_date__date_gte=start_date, transaction_date__date_lte=end_date)

            # calculating the filtered transactions balance
            self.balance = Transaction.objects.filter(transaction_date__date_gte=start_date, transaction_date__date_lte=end_date).aggregate(
                # amount__sum is the key of the dictionary returned by aggregate method. we can also use balance=Sum('amount') but then we have to use balance.balance to access the balance in the template. so we use amount__sum (Note: comment will be updated later!)
                balance=Sum('amount'))['amount__sum']
        else:
            # by default calculating the balance of all transactions
            self.balance = self.request.user.account.balance

        # return queryset
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
        })
        return context


class Repayment(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        if loan.loan_approved:
            customer = loan.account
            if loan.amount < customer.balance:
                customer.balance -= loan.amount
                loan.balance_after_transaction = customer.balance
                customer.save()
                loan.transaction_type = 'Repayment'
                loan.save()

                messages.success(
                    request, f'You have successfully repaid ${loan.amount}')

                return redirect('transaction_report')
            else:
                messages.error(
                    request, f'You have insufficient balance to repay ${loan.amount}')

                return redirect('transaction_report')


class LoanList(LoginRequiredMixin, ListView):
    template_name = ''
    model = Transaction
    context_object_name = 'loans'

    def get_queryset(self):
        customer = self.request.user.account
        queryset = Transaction.objects.filter(
            account=customer, transaction_type='Loan')
        return queryset
