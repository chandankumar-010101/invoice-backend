from drf_yasg import openapi

email_invoice_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'cc':  openapi.Parameter('cc email list',
            in_=openapi.IN_QUERY,
            description='CC email list',
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_STRING),
            required=True
        ),
        'subject': openapi.Schema(type=openapi.TYPE_STRING),
        'body': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['subject','cc','body']
)


send_reminder_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'subject': openapi.Schema(type=openapi.TYPE_STRING),
        'body': openapi.Schema(type=openapi.TYPE_STRING),
        'is_whatsapp': openapi.Schema(type=openapi.TYPE_STRING),
        'is_email': openapi.Schema(type=openapi.TYPE_STRING),

    },
    required=['subject','is_whatsapp','body','is_email']
)

whats_invoice_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'to': openapi.Schema(type=openapi.TYPE_STRING),
        'additional': openapi.Schema(type=openapi.TYPE_STRING),
        'body': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['to','body','additional']
)

record_payment_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'payment_mode': openapi.Schema(type=openapi.TYPE_STRING),
        'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
        'payment_date':openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['payment_mode','amount','payment_date']
)


payment_method_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'is_bank_transfer': openapi.Schema(type=openapi.TYPE_STRING),
        'is_card_payment': openapi.Schema(type=openapi.TYPE_STRING),
        'is_mobile_money': openapi.Schema(type=openapi.TYPE_STRING),
        'auto_payment_reminder': openapi.Schema(type=openapi.TYPE_STRING),
    }
)


roles_permissions_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'roles':  openapi.Parameter('Roles',
            in_=openapi.IN_QUERY,
            description='Roles',
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_OBJECT),
            required=True
        ),
    },
    required=['roles',]
)


card_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'payment_type': openapi.Schema(type=openapi.TYPE_STRING),
        'holder_name': openapi.Schema(type=openapi.TYPE_STRING),
        'card_number': openapi.Schema(type=openapi.TYPE_STRING),
        'expiry_month': openapi.Schema(type=openapi.TYPE_STRING),
        'expiry_year': openapi.Schema(type=openapi.TYPE_STRING),
        'cvv_code': openapi.Schema(type=openapi.TYPE_STRING),
        'card_type': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['payment_type','holder_name','card_number','expiry_month','expiry_year','cvv_code','card_type']

)

mpesa_schema =openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'm_pesa': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['m_pesa',]

)