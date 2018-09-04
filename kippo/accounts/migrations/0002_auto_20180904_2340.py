# Generated by Django 2.1.1 on 2018-09-04 14:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('accounts', '0001_initial'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kippoorganization',
            name='default_columnset',
            field=models.ForeignKey(blank=True, default=None, help_text='If defined, this will be set as the default ColumnSet when a Project is created', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='projects.ProjectColumnSet'),
        ),
        migrations.AddField(
            model_name='kippoorganization',
            name='updated_by',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='accounts_kippoorganization_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='emaildomain',
            name='created_by',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='accounts_emaildomain_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='emaildomain',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.KippoOrganization'),
        ),
        migrations.AddField(
            model_name='emaildomain',
            name='updated_by',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='accounts_emaildomain_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='kippouser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='kippouser',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.KippoOrganization'),
        ),
        migrations.AddField(
            model_name='kippouser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='kippoorganization',
            unique_together={('name', 'github_organization_name')},
        ),
    ]