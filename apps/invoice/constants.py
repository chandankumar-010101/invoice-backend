INVOICE_STATUS = (
    ('SENT', 'Sent'),
    ('PAYMENT_SCHEDULED', 'Payment Scheduled'),
    ('UNSENT', 'Unsent'),
    ('PAYMENT_DONE', 'Payment Done'),

)


PAYMENT_TYPE = (
    ('Manually', 'Manually'),
    ('Online', 'Online'),
)


PAYMENT_MODE = (
    ('Cash', 'Cash'),
    ('Cheque', 'Cheque'),
    ('Bank Transfer', 'Bank Transfer'),
    ('M-Pesa', 'M-Pesa'),
    ('Debit Card', 'Debit Card'),
    ('Other', 'Other'),
)