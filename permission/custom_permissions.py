from rest_framework import permissions
from permission.models import Permission

class RoleBasedPermission(permissions.BasePermission):
    """
    Custom permission to dynamically check user roles based on view action.
    Naming convention: basename_action (e.g., 'permission_list', 'user_create')
    """
    
    def has_permission(self, request, view):
        # 1. User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # 2. Superusers bypass all permission checks
        if getattr(request.user, 'is_superuser', False):
            return True
            
        # 3. Check if user has a role assigned
        if not getattr(request.user, 'role', None):
            return False
            
        # 4. Determine the required permission name dynamically
        basename = getattr(view, 'basename', view.__class__.__name__.lower())
        action = getattr(view, 'action', request.method.lower())
        
        required_permission = f"{basename}_{action}"
        
        # 5. Check in the database if this role has this permission active
        has_perm = Permission.objects.filter(
            role=request.user.role,
            permission_name=required_permission,
            status=True
        ).exists()
        
        return has_perm
