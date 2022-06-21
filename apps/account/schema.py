from drf_yasg import openapi

login_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
        'company_name': openapi.Schema(type=openapi.TYPE_STRING),
        'industry': openapi.Schema(type=openapi.TYPE_STRING),
        'annual_turnover': openapi.Schema(type=openapi.TYPE_STRING),
        'accounting_software': openapi.Schema(type=openapi.TYPE_STRING),
        'invoice_issue_month': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['first_name','last_name','email','phone_number','company_name'
        ,'industry','annual_turnover','accounting_software','invoice_issue_month','password'
    ]
)

login_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['email','password']
)

change_password_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'current_password': openapi.Schema(type=openapi.TYPE_STRING),
        'new_password': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['current_password','new_password']
)