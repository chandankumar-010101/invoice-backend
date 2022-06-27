from cmath import pi
from rest_framework.permissions import BasePermission
import apps.account.response_messages as resp_msg


class IsAdminOnly(BasePermission):

    message = resp_msg.NOT_ADMIN

    def has_permission( self, request, view ):
        
        if request.user.user_type != 2:
            self.message = resp_msg.ADMIN_ONLY_PERMISSION
            return False
        return True