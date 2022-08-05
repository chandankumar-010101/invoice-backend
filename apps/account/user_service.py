import profile
from django.contrib.auth import get_user_model
from .models import Organization
from .models import UserProfile
from .utils import generate_organization_code


def create_organization(request):
    """ Create an organization. 
    
    Args:
        request: request object
    Return:
        org: organization object
    """
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
    """ Create a user profile 
    
    Args:
        request: request object
    Return:
        org: profile object
    """
    if request.data.get('first_name') is None and request.data.get('last_name') is None:
        full_name = request.data.get('full_name')
    else:
        full_name = request.data.get('first_name')+' '+request.data.get('last_name')

    profile = UserProfile.objects.create(
        full_name=full_name,
        email=request.data.get('email'),
        phone=request.data.get('phone_number'),
        user=user,
        organization=org,
        is_verified=True
    )
    return profile

def create_admin_user(request, user_type):
    """ Create a admin user while registration 
    
    Args:
        request:create_admin_user request object
    Return:
        user: organization object
    """
    User = get_user_model()
    email = request.data.get('email')
    password = request.data.get('password')
    user = User.objects.create_user(email, password, user_type=user_type)
    return user

def create_user_with_role(request):
    """ Create an user for organization with role.
    
    Args:password
        request: request object
    Return:
        user: organization object
    """
    User = get_user_model()
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role')
    user = User.objects.create_user(email, password, user_type=role)
    return user
