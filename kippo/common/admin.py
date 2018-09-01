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


class KippoAdminSite(admin.AdminSite):
    # update displayed header/title
    site_header = settings.SITE_HEADER
    site_title = settings.SITE_TITLE


admin_site = KippoAdminSite(name='kippoadmin')
