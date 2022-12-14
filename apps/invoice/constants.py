INVOICE_STATUS = (
    ('SENT', 'Sent'),
    ('PAYMENT_SCHEDULED', 'Payment Scheduled'),
    ('UNSENT', 'Unsent'),
    ('PAYMENT_DONE', 'Payment Done'),
    ('PARTIALLY_PAID', 'Partially Paid'),
)

PAYMENT_TYPE = (
    ('Manually', 'Manually'),
    ('Online', 'Online'),
)

PAYMENT_MODE = (
    ('Cash', 'Cash'),
    ('Cheque', 'Cheque'),
    ('Card', 'Card'),
    ('Bank Transfer', 'Bank Transfer'),
    ('M-Pesa', 'M-Pesa'),
    ('Debit Card', 'Debit Card'),
    ('Other', 'Other'),
)

REMINDER_TYPE = (
    ('Due In','Due In'),
    ('Overdue By','Overdue By')
)

PAYMENT_TYPE_CHOICES =(
    (1 ,'Credit/Debit/Atm'),
    (2,'M-Pesa'),
)