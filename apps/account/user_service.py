from django.contrib.auth import get_user_model
from .models import Organization

def create_organization(request):
    org = Organization.objects.create(company_name = request.data.get('company_name'), 
                            email = request.data.get('email'),
                            industry=request.data.get('industry'), 
                            annual_turnover=request.data.get('annual_turnover'),
                            accounting_software=request.data.get('accounting_software'), 
                            estimate_invoice_issue=request.data.get('invoice_issue_month')
                        )
    return org


def create_admin_user(request):
    User = get_user_model()
    email = request.data.get('email_address')
    password = request.data.get('password')
    user = User.objects.create_user(email, password, user_type=2)
    return user

