from collections import Counter

from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required

from projects.models import KippoProject
from .models import KippoTask, KippoTaskStatus


# TODO: Fix support
# -- Initially used to separate general meeting tasks from development tasks
# -- Consider how this should be handled moving forward (general meeting tasks are not being managed atm)
EXCLUDE_TASK_CATEGORIES = []
DEFAULT_TASK_DISPLAY_STATE = settings.DEFAULT_TASK_DISPLAY_STATE


def assignee_project_keyfunc(task_object: KippoTask) -> tuple:
    """
    A keying function that returns the values to use for sorting
    :param task_object:
    :return: (task_object.assignee.username, task_object.project.name)
    """
    username = ''
    if task_object.assignee:
        username = task_object.assignee.username

    project = ''
    if task_object.project:
        project = task_object.project.name

    return username, project


@staff_member_required
def view_inprogress_task_status(request):
    github_login = request.GET.get('github_login', None)
    display_state_filter = request.GET.get('state', None)
    # Collect tasks with TaskStatus updated this last 2 weeks
    two_weeks_ago = timezone.timedelta(days=14)
    active_taskstatus_startdate = (timezone.now() - two_weeks_ago).date()

    active_projects = KippoProject.objects.filter(is_closed=False).order_by('name')

    # TODO: fix so that done columns is accurately applied per project
    # --> Temporary Workaround
    # --> This will work IF all projects share the same 'Done' state,
    # --> But does NOT support project defined done/active state properly!!!
    done_column_names = []
    for project in KippoProject.objects.filter(is_closed=False):
        done_column_names.extend(project.columnset.get_done_column_names())
    done_column_names = list(set(done_column_names))

    task_state_counts = {r['state']: r['state__count'] for r in KippoTaskStatus.objects.filter(effort_date__gte=active_taskstatus_startdate).values('state').order_by('state').annotate(Count('state'))}
    total_state_count = sum(task_state_counts.values())
    task_state_counts['total'] = total_state_count

    # debug
    print(KippoTaskStatus.objects.filter(state='in-progress'))

    # Removed Exclude Categories
    if not display_state_filter:
        display_state_filter = DEFAULT_TASK_DISPLAY_STATE

    # NOTE: done can not be
    active_taskstatus = KippoTaskStatus.objects.filter(effort_date__gte=active_taskstatus_startdate,
                                                       state=display_state_filter,
                                                       task__github_issue_api_url__isnull=False,  # filter out non-linked tasks
                                                       task__assignee__is_developer=True).exclude(task__project__is_closed=True)

    # apply specific user filter if defined
    if github_login:
        active_taskstatus = active_taskstatus.filter(task__assignee__github_login=github_login)

    # collect unique Tasks
    collected_task_ids = []
    unique_tasks = []
    for taskstatus in active_taskstatus:
        if taskstatus.task.id not in collected_task_ids:
            unique_tasks.append(taskstatus.task)
            collected_task_ids.append(taskstatus.task.id)

    # get user totals
    user_effort_totals = Counter()
    for task in unique_tasks:
        if task.assignee:
            days_remaining = task.effort_days_remaining() if task.effort_days_remaining() else 0
            user_effort_totals[task.assignee.username] += days_remaining

    # sort tasks by assignee.username, project.name
    sorted_tasks = sorted(unique_tasks, key=assignee_project_keyfunc)
    return render(request, 'tasks/view_inprogress_task_status.html', {'tasks': sorted_tasks,
                                                                      'active_projects': active_projects,
                                                                      'user_effort_totals': dict(user_effort_totals),
                                                                      'task_state_counts': task_state_counts})
