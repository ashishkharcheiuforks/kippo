from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from social_django.models import Association, Nonce, UserSocialAuth
from common.admin import UserCreatedBaseModelAdmin, AllowIsStaffAdminMixin
from octocat.models import GithubAccessToken
from .models import EmailDomain, KippoOrganization, KippoUser, OrganizationMembership, PersonalHoliday


class EmailDomainAdminReadOnlyInline(admin.TabularInline):
    model = EmailDomain
    extra = 0
    fields = (
        'domain',
        'is_staff_domain',
        'updated_by',
        'updated_datetime',
        'created_by',
        'created_datetime',
    )
    readonly_fields = (
        'domain',
        'is_staff_domain',
        'updated_by',
        'updated_datetime',
        'created_by',
        'created_datetime',
    )

    def has_add_permission(self, request, obj):  # so that 'add button' is not available in admin
        return False

    def get_queryset(self, request):
        # update so that Milestones are displayed in expected delivery order
        qs = super().get_queryset(request).order_by('created_datetime')
        return qs


class EmailDomainAdminInline(admin.TabularInline):
    model = EmailDomain
    extra = 0
    fields = (
        'domain',
        'is_staff_domain',
    )

    def get_queryset(self, request):
        # clear the queryset so that no EDITABLE entries are displayed
        qs = super().get_queryset(request).none()
        return qs


class GithubAccessTokenAdminReadOnlyInline(admin.StackedInline):
    model = GithubAccessToken
    exclude = ('token', )
    fields = (
        'created_by',
        'created_datetime',
    )
    readonly_fields = (
        'created_by',
        'created_datetime',
    )

    def has_add_permission(self, request, obj):
        return False


class GithubAccessTokenAdminInline(admin.StackedInline):
    model = GithubAccessToken
    extra = 0

    def get_queryset(self, request):
        # clear the queryset so that no EDITABLE entries are displayed
        qs = super().get_queryset(request).none()
        return qs

    def has_add_permission(self, request, obj):
        return True


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(UserCreatedBaseModelAdmin):
    list_display = (
        'organization',
        'user',
        'is_project_manager',
        'is_developer',
    )
    ordering = (
        'organization',
        'user',
    )


@admin.register(KippoOrganization)
class KippoOrganizationAdmin(UserCreatedBaseModelAdmin):
    list_display = (
        'name',
        'github_organization_name',
        'default_task_category',
        'updated_by',
        'updated_datetime',
        'created_by',
        'created_datetime',
    )
    search_fields = (
        'name',
    )
    inlines = (
        GithubAccessTokenAdminReadOnlyInline,
        GithubAccessTokenAdminInline,
        EmailDomainAdminReadOnlyInline,
        EmailDomainAdminInline,
    )


@admin.register(KippoUser)
class KippoUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'github_login',
        'get_github_organizations',
        'last_name',
        'first_name',
        'date_joined',
        'last_login',
        'is_github_outside_collaborator',
        'is_staff',
        'is_superuser',
    )
    exclude = ('user_permissions', 'groups', 'last_login', )

    def get_is_collaborator(self, obj):
        return obj.is_github_outside_collaborator
    get_is_collaborator.short_description = _('Is Collaborator')

    def get_github_organizations(self, obj):
        membership_organizations = []
        for organization in obj.memberships.all():
            name = organization.github_organization_name
            membership_organizations.append(name)
        return ', '.join(membership_organizations)
    get_github_organizations.short_description = _('Github Organizations')


@admin.register(PersonalHoliday)
class PersonalHolidayAdmin(AllowIsStaffAdminMixin, admin.ModelAdmin):
    list_display = (
        'user',
        'is_half',
        'day',
        'duration',
    )

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'pk', None) is None:
            obj.user = request.user
        obj.save()


admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)
