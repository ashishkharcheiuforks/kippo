from django.contrib import admin
from django.conf import settings


class UserCreatedBaseModelAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'pk', None) is None:
            obj.created_by = request.user
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if instance.id is None:
                instance.created_by = request.user  # only update created_by once!

            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()


class AllowIsStaffAdminMixin:

    def check_perm(self, user_obj):
        if not user_obj.is_active or user_obj.is_anonymous:
            return False
        if user_obj.is_superuser or user_obj.is_staff:
            return True
        return False

    def has_add_permission(self, request):
        return self.check_perm(request.user)

    def has_change_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_delete_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_module_permission(self, request, obj=None):
        return self.check_perm(request.user)


class AllowIsStaffReadonlyMixin:

    def check_perm(self, user_obj):
        if not user_obj.is_active or user_obj.is_anonymous:
            return False
        if user_obj.is_superuser or user_obj.is_staff:
            return True
        return False

    def has_add_permission(self, request):
        if not request.user.is_active or request.user.is_anonymous:
            return False
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        if not request.user.is_active or request.user.is_anonymous:
            return False
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_active or request.user.is_anonymous:
            return False
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_module_permission(self, request, obj=None):
        return self.check_perm(request.user)


class AllowIsSuperuserAdminMixin:

    def check_perm(self, user_obj):
        if not user_obj.is_active or user_obj.is_anonymous:
            return False
        if user_obj.is_superuser:
            return True
        return False

    def has_add_permission(self, request):
        return self.check_perm(request.user)

    def has_change_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_delete_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_module_permission(self, request, obj=None):
        return self.check_perm(request.user)


class OrganizationTaskQuerysetModelAdminMixin:

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(project__organization__in=request.user.organizations).order_by('project__organization').distinct()


class OrganizationQuerysetModelAdminMixin:

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # get user organizations
        return qs.filter(organizationmembership__organization__in=request.user.organizations).order_by('organizationmembership__organization').distinct()


class KippoAdminSite(admin.AdminSite):
    # update displayed header/title
    site_header = settings.SITE_HEADER
    site_title = settings.SITE_TITLE


admin_site = KippoAdminSite(name='kippoadmin')
