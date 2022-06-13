import string
import random
from rest_framework_simplejwt.tokens import RefreshToken


def generate_organization_code():
    """ Generate random 10 digit code for the organization. """

    org_code = 'IP'+''.join(random.choices(string.ascii_uppercase, k = 8))
    return org_code

def get_jwt_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }