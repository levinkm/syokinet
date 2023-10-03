from rest_framework import permissions

class IsAdminUserOrIsAuthenticatedReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' and request.user.is_authenticated and request.user.is_admin:
            return True
    
        if request.method == 'GET' and request.user.is_authenticated:
            return True
        
        if request.method == 'DELETE' and request.user.is_authenticated and request.user.is_admin:
            return True
        
        if request.method == 'PUT' and request.user.is_authenticated and request.user.is_admin:
            return True

        return False
    
    