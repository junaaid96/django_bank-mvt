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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Create your views here.

# we will inherit this view for all transaction such as deposit, withdrawal, transfer, loan request, etc.


def send_transaction_email(user, email, amount, mail_subject, html_template):
    message = render_to_string(html_template, {
        'user': user,
        'amount': amount
    })
    send_email = EmailMultiAlternatives(mail_subject, '', to=[email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class CreateTransactionView(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction-report')

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

        send_transaction_email(
            self.request.user, self.request.user.email, amount, 'Deposit Confirmation', 'email/deposit_email.html'
        )

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

        send_transaction_email(
            self.request.user, self.request.user.email, amount, 'Withdrawal Confirmation', 'email/withdraw_email.html'
        )

        return super().form_valid(form)


class TransferMoney(CreateTransactionView):
    pass


class LoanRequest(CreateTransactionView):
    form_class = LoanRequestForm
    title = 'Loan Request'

    def get_initial(self):
        initial = {'transaction_type': 'Loan'}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        loan_count = Transaction.objects.filter(
            account=self.request.user.account, transaction_type='Loan', loan_repayment=False).count()

        if loan_count >= 3:
            return HttpResponse('You have reached the maximum limit of loan request')

        messages.success(
            self.request, f'You have successfully requested ${amount} loan and awaiting for admin approval')
        
        send_transaction_email(
            self.request.user, self.request.user.email, amount, 'Loan Request', 'email/loan_request_email.html'
        )

        return super().form_valid(form)


class TransactionReport(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0
    # if i didn't use context_object_name, then i have to use object_list in the template.
    context_object_name = 'transactions'

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
                timestamp__date__gte=start_date, timestamp__date__lte=end_date)

            # calculating the filtered transactions balance
            self.balance = Transaction.objects.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date).aggregate(
                # amount__sum is the key of the dictionary returned by aggregate method. we can also use balance=Sum('amount') but then we have to use balance.balance to access the balance in the template. so we use amount__sum (Note: comment will be updated later!)
                Sum('amount'))['amount__sum']
        else:
            # by default calculating the balance of all transactions
            self.balance = self.request.user.account.balance

        # return queryset.distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
        })
        return context


class LoanRepayment(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        if loan.loan_approved:
            customer = loan.account
            if loan.amount <= customer.balance:
                customer.balance -= loan.amount
                # loan.balance_after_transaction = customer.balance (this line is not needed because we are creating new transaction instead of updating the loan transaction)
                customer.save()
                # loan.transaction_type = 'Repayment' (also not needed because we are creating new transaction instead of updating the loan transaction)
                loan.loan_repayment = True
                loan.save()

                # creating the new repayment transaction instead of updating the loan transaction
                Transaction.objects.create(
                    account=loan.account,
                    amount=loan.amount,
                    balance_after_transaction=customer.balance,
                    transaction_type='Repayment'
                )

                messages.success(
                    request, f'You have successfully repaid ${loan.amount}')
                
                send_transaction_email(
                    request.user, request.user.email, loan.amount, 'Loan Repayment Confirmation', 'email/loan_repayment_email.html'
                )

                return redirect('transaction-report')
            else:
                messages.error(
                    request, f'You have insufficient balance to repay ${loan.amount}')

                return redirect('transaction-report')


class LoanList(LoginRequiredMixin, ListView):
    template_name = 'transactions/loan_lists.html'
    model = Transaction
    context_object_name = 'loans'

    def get_queryset(self):
        customer = self.request.user.account
        loan_queryset = Transaction.objects.filter(
            account=customer, transaction_type='Loan')

        return loan_queryset
