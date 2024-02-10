from django import forms
from .models import Transaction
from decimal import Decimal


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']

    def __init__(self, *args, **kwargs):
        # we will pass account object from view to form. so we need to pop it from kwargs.
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        # we will handle this field in view so we disable it for user.
        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        # we are assigning account object to transaction instance.
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        min_deposit = 1000
        if amount < min_deposit:
            raise forms.ValidationError(
                f"Minimum deposit amount is ${min_deposit:,.2f}")
        return amount


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        balance = account.balance
        min_withdraw = 1000
        max_withdraw = 5000000
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw:
            raise forms.ValidationError(
                f"Minimum withdraw amount is ${min_withdraw:,.2f}")
        if amount > max_withdraw:
            raise forms.ValidationError(
                f"Maximum withdraw amount is ${max_withdraw:,.2f}")
        if amount > balance:
            raise forms.ValidationError(
                f"Insufficient balance. Your balance is ${balance:,.2f}")
        return amount


class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        balance = account.balance
        min_loan = balance * Decimal('0.1')  # Convert float to Decimal
        max_loan = balance * Decimal('0.5')
        amount = self.cleaned_data.get('amount')
        if amount < min_loan:
            raise forms.ValidationError(
                f"You have to take minimum ${min_loan:,.2f} loan")
        if amount > max_loan:
            raise forms.ValidationError(
                f"You can take maximum ${max_loan:,.2f} loan")
        return amount
