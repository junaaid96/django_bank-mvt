from django.contrib import admin
from transactions.views import send_transaction_email
from .models import Transaction

# Register your models here.
# admin.site.register(Transaction)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'transaction_type',
                    'balance_after_transaction', 'timestamp', 'loan_approved']

    def save_model(self, request, obj, form, change):
        if obj.transaction_type == 'Deposit':
            obj.account.balance += obj.amount
        elif obj.transaction_type == 'Withdraw':
            if obj.account.balance >= obj.amount:
                obj.account.balance -= obj.amount
            else:
                raise ValueError('Insufficient account balance.')
        elif obj.transaction_type == 'Loan':
            if obj.loan_approved:
                obj.account.balance += obj.amount
                obj.balance_after_transaction += obj.amount
                send_transaction_email(
                    obj.account.user, obj.account.user.email, obj.amount, 'Loan Approval', 'email/loan_approved_email.html'
                )
            else:
                raise ValueError('Loan transaction is not approved.')
        elif obj.transaction_type == 'Repayment':
            if obj.account.balance >= obj.amount:
                obj.account.balance -= obj.amount
            else:
                raise ValueError('Insufficient account balance for repayment.')

        obj.balance_after_transaction = obj.account.balance
        obj.account.save()
        super().save_model(request, obj, form, change)
