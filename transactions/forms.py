from django import forms
from .models import Transaction
from decimal import Decimal
from accounts.models import UserBankAccount


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
        min_deposit = 100
        max_deposit = 500000
        if amount < min_deposit:
            raise forms.ValidationError(
                f"Minimum deposit amount is ${min_deposit:,.2f}")
        if amount > max_deposit:
            raise forms.ValidationError(
                f"Maximum deposit amount is ${max_deposit:,.2f}")
        return amount


class TransferForm(TransactionForm):
    receiver_account_no = forms.IntegerField()

    def clean_amount(self):
        account = self.account
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        if amount < 50:
            raise forms.ValidationError("Minimum transfer amount is $50")
        if amount > balance:
            raise forms.ValidationError(
                f"Insufficient balance. Your balance is ${balance:,.2f}")
        return amount

    def clean_receiver_account_no(self):
        receiver_account_no = self.cleaned_data.get('receiver_account_no')
        try:
            receiver_account = UserBankAccount.objects.get(
                account_no=receiver_account_no)
        except UserBankAccount.DoesNotExist:
            raise forms.ValidationError("Invalid account number!")
        return receiver_account


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        balance = account.balance
        min_withdraw = 100
        max_withdraw = 100000
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
