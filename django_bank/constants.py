# ACCOUNT_TYPE is a tuple of tuples. using tuple for choices. first value of tuple will be stored in database and the second value is for displaying.
ACCOUNT_TYPE = (
    ('Saving', 'Saving'),
    ('Current', 'Current'),
    ('Fixed', 'Fixed'),
)

GENDER_TYPE = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)

TRANSACTION_TYPE = (
    ('Deposit', 'Deposit'),
    ('Receive', 'Receive'),
    ('Withdraw', 'Withdraw'),
    ('Transfer', 'Transfer'),
    ('Loan', 'Loan'),
    ('Repayment', 'Repayment'),
)
