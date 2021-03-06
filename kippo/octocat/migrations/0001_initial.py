# Generated by Django 2.2.3 on 2019-07-29 19:21

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import octocat.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GithubRepositoryLabelSet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Reference Name For LabelSet', max_length=120)),
                ('labels', django.contrib.postgres.fields.jsonb.JSONField(help_text='Labels defined in the format: [{"name": "category:X", "description": "", "color": "AED6F1"},]')),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='GithubWebhookEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(choices=[('unprocessed', 'unprocessed'), ('processing', 'processing'), ('processed', 'processed')], default='unprocessed', max_length=15)),
                ('event', django.contrib.postgres.fields.jsonb.JSONField()),
                ('organization', models.ForeignKey(help_text='Organization to which event belongs to', on_delete=django.db.models.deletion.CASCADE, to='accounts.KippoOrganization')),
                ('related_project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.KippoProject')),
            ],
        ),
        migrations.CreateModel(
            name='GithubRepository',
            fields=[
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(auto_now=True)),
                ('closed_datetime', models.DateTimeField(editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Github Repository Name')),
                ('api_url', models.URLField(help_text='Github Repository API URL')),
                ('html_url', models.URLField(help_text='Github Repository HTML URL')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='octocat_githubrepository_created_by', to=settings.AUTH_USER_MODEL)),
                ('label_set', models.ForeignKey(blank=True, help_text='Github Repository LabelSet', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='octocat.GithubRepositoryLabelSet')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.KippoOrganization')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='octocat_githubrepository_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'github repositories',
                'unique_together': {('name', 'api_url', 'html_url')},
            },
        ),
        migrations.CreateModel(
            name='GithubOrganizationalWebhook',
            fields=[
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(auto_now=True)),
                ('closed_datetime', models.DateTimeField(editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('hook_id', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('events', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=15), default=octocat.models.webhook_events_default, help_text='Github webhook event(s)', size=None)),
                ('url', models.URLField(default='http://127.0.0.1/octocat/webhook/', help_text='The endpoint which github will send webhook events to')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='octocat_githuborganizationalwebhook_created_by', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.KippoOrganization')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='octocat_githuborganizationalwebhook_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GithubAccessToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(auto_now=True)),
                ('closed_datetime', models.DateTimeField(editable=False, null=True)),
                ('token', models.CharField(help_text='Github Personal Token for accessing Github Projects, Milestones, Repositories and Issues', max_length=40)),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='octocat_githubaccesstoken_created_by', to=settings.AUTH_USER_MODEL)),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounts.KippoOrganization')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='octocat_githubaccesstoken_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GithubMilestone',
            fields=[
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(auto_now=True)),
                ('closed_datetime', models.DateTimeField(editable=False, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('number', models.PositiveIntegerField(editable=False, help_text='Github Milestone Number (needed for update/delete on github)', verbose_name='Github Milestone Number')),
                ('api_url', models.URLField(blank=True, default=None, help_text='Github Repository Milestone API URL', null=True, verbose_name='Github Milestone API URL')),
                ('html_url', models.URLField(blank=True, default=None, help_text='Github Repository Milestone HTML URL', null=True, verbose_name='Github Milestone HTML URL')),
                ('created_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='octocat_githubmilestone_created_by', to=settings.AUTH_USER_MODEL)),
                ('milestone', models.ForeignKey(help_text='Related Kippo Milestone', on_delete=django.db.models.deletion.CASCADE, to='projects.KippoMilestone', verbose_name='Kippo Milestone')),
                ('repository', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='octocat.GithubRepository')),
                ('updated_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='octocat_githubmilestone_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('milestone', 'repository', 'number')},
            },
        ),
    ]
