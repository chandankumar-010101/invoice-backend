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

record_payment_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, responses={200: 'OK'}, properties={
        'payment_mode': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['payment_mode',]
)