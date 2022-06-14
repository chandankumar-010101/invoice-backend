import profile
from django.contrib.auth import get_user_model
from .models import Organization
from .models import UserProfile
from .utils import generate_organization_code


def create_organization(request):
    org = Organization.objects.create(company_name = request.data.get('company_name'), 
                            code = generate_organization_code(),
                            email = request.data.get('email'),
                            industry=request.data.get('industry'), 
                            annual_turnover=request.data.get('annual_turnover'),
                            accounting_software=request.data.get('accounting_software'), 
                            estimate_invoice_issue=request.data.get('invoice_issue_month'),
                            phone_number=request.data.get('phone_number')
                        )
    return org

def create_user_profile(request, user, org):

    full_name = request.data.get('first_name')+' '+request.data.get('last_name')
    profile = UserProfile.objects.create(
                            full_name=full_name,
                            email=request.data.get('email'),
                            phone=request.data.get('phone_number'),
                            user=user,
                            organization=org,
                            is_verified=True)
    return profile

def create_admin_user(request, user_type):
    User = get_user_model()
    email = request.data.get('email')
    password = request.data.get('password')
    user = User.objects.create_user(email, password, user_type=user_type)
    return user

