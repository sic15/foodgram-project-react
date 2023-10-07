from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorChangeOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
