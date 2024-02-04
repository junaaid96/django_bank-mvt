from django.urls import path
from .views import DepositMoney, WithdrawMoney, LoanRequest, LoanRepayment, TransactionReport, LoanList

urlpatterns = [
    path('deposit/', DepositMoney.as_view(), name='deposit'),
    path('withdraw/', WithdrawMoney.as_view(), name='withdraw'),
    path('loan-request/', LoanRequest.as_view(), name='loan-request'),
    path('loan-repayment/<int:loan_id>/', LoanRepayment.as_view(), name='loan-repayment'),
    path('transaction-report/', TransactionReport.as_view(),
         name='transaction-report'),
    path('loan-list/', LoanList.as_view(), name='loan-list'),
]
