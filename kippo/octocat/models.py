import uuid
from django.db import models
from django.contrib.postgres import fields
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField

from common.models import UserCreatedBaseModel
from accounts.models import KippoOrganization


GITHUB_MILESTONE_CLOSE_STATE = 'closed'
GITHUB_REPOSITORY_NAME_MAX_LENGTH = 100


class GithubRepositoryLabelSet(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    organization = models.ForeignKey(
        KippoOrganization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_('Organization to which the labelset belongs to.')
    )
    name = models.CharField(max_length=120,
                            help_text=_('Reference Name For LabelSet'))
    labels = JSONField(help_text='Labels defined in the format: '
                                 '[{"name": "category:X", "description": "", "color": "AED6F1"},]')
    created_datetime = models.DateTimeField(auto_now_add=True,
                                            editable=False)
    updated_datetime = models.DateTimeField(auto_now=True,
                                            editable=False)

    def __str__(self):
        return f'{self.__class__.__name__}({self.id}) {self.name}'


class GithubRepository(UserCreatedBaseModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    organization = models.ForeignKey(KippoOrganization,
                                     on_delete=models.CASCADE)
    name = models.CharField(max_length=GITHUB_REPOSITORY_NAME_MAX_LENGTH,
                            verbose_name=_('Github Repository Name'))
    label_set = models.ForeignKey(GithubRepositoryLabelSet,
                                  on_delete=models.DO_NOTHING,
                                  null=True,
                                  blank=True,
                                  help_text=_('Github Repository LabelSet'))
    api_url = models.URLField(help_text=_('Github Repository API URL'))
    html_url = models.URLField(help_text=_('Github Repository HTML URL'))

    def __str__(self):
        return f'{self.__class__.__name__}({self.name}) html_url={self.html_url}'

    class Meta:
        verbose_name_plural = _('github repositories')
        unique_together = (
            'name',
            'api_url',
            'html_url',
        )


class GithubMilestone(UserCreatedBaseModel):
    """
    For managing linkage with Github Repository Milestones
    A single KippoProject (and Github Organizational Project) may link to multiple Github Repositories.
    Therefore multiple GithubMilestone objects may exist for a single KippoMilestone,
    in order to represent a single *logical* milestone across multiple Github Repositories.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    milestone = models.ForeignKey('projects.KippoMilestone',
                                  verbose_name=_('Kippo Milestone'),
                                  on_delete=models.CASCADE,
                                  help_text=_('Related Kippo Milestone'))
    repository = models.ForeignKey(GithubRepository,
                                   null=True,
                                   default=None,
                                   on_delete=models.CASCADE)
    number = models.PositiveIntegerField(_('Github Milestone Number'),
                                         editable=False,
                                         help_text=_('Github Milestone Number (needed for update/delete on github)'))
    api_url = models.URLField(_('Github Milestone API URL'),
                              null=True,
                              blank=True,
                              default=None,
                              help_text=_('Github Repository Milestone API URL'))
    html_url = models.URLField(_('Github Milestone HTML URL'),
                               null=True,
                               blank=True,
                               default=None,
                               help_text=_('Github Repository Milestone HTML URL'))

    class Meta:
        unique_together = ('milestone', 'repository', 'number')


class GithubAccessToken(UserCreatedBaseModel):
    organization = models.OneToOneField('accounts.KippoOrganization',
                                        on_delete=models.CASCADE)
    token = models.CharField(max_length=40,
                             help_text=_("Github Personal Token for accessing Github Projects, Milestones, Repositories and Issues"))

    def __str__(self):
        return f'{self.__class__.__name__}({self.organization.name} [{self.organization.github_organization_name}])'


def webhook_events_default():
    return ['project', 'project_card']


class GithubOrganizationalWebhook(UserCreatedBaseModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    organization = models.ForeignKey('accounts.KippoOrganization',
                                     on_delete=models.CASCADE)
    hook_id = models.PositiveSmallIntegerField(null=True,
                                               blank=True)
    events = fields.ArrayField(default=webhook_events_default,
                               base_field=models.CharField(max_length=15),
                               help_text=_('Github webhook event(s)'))
    url = models.URLField(default=settings.WEBHOOK_URL,
                          help_text=_('The endpoint which github will send webhook events to'))


WEBHOOK_EVENT_STATES = (
    ('unprocessed', 'unprocessed'),
    ('processing', 'processing'),
    ('error', 'error'),
    ('processed', 'processed'),
    ('ignore', 'ignore'),
)


class GithubWebhookEvent(models.Model):
    organization = models.ForeignKey(
        'accounts.KippoOrganization',
        on_delete=models.CASCADE,
        help_text=_('Organization to which event belongs to')
    )
    created_datetime = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    updated_datetime = models.DateTimeField(
        auto_now=True,
        editable=False
    )
    state = models.CharField(
        max_length=15,
        default='unprocessed',
        choices=WEBHOOK_EVENT_STATES
    )
    event_type = models.CharField(
        max_length=25,
        null=True,
        help_text=_('X-Github-Event value (See: https://developer.github.com/v3/activity/events/types/)')
    )
    event = fields.JSONField(editable=False)

    def __str__(self):
        return f'GithubWebhookEvent({self.organization.name}:{self.event_type}:{self.created_datetime}:{self.state})'
