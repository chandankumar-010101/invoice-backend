import string
import random


def generate_organization_code():
    """ Generate random 10 digit code for the organization. """

    org_code = 'IP'+''.join(random.choices(string.ascii_uppercase, k = 8))
    return org_code