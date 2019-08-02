import json
import hmac
import hashlib
import logging
import urllib.parse
from http import HTTPStatus
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from .functions import queue_incoming_project_card_event
from .models import KippoOrganization


logger = logging.getLogger(__name__)


def validate_webhook_request(request: HttpRequest, organization: KippoOrganization) -> True:
    """
    Validate the contents with the registered secret
    https://developer.github.com/webhooks/securing/#validating-payloads-from-github
    """
    secret = organization.webhook_secret.encode('utf8')
    payload = request.body
    calculated_signature = hmac.new(
        key=secret,
        msg=payload,
        digestmod=hashlib.sha1
    ).hexdigest()
    local_signature = f'sha1={calculated_signature}'
    github_signature = request.META.get('HTTP_X_HUB_SIGNATURE', None)
    if not github_signature:
        github_signature = request.META.get('X-Hub-Signature', None)
    if not github_signature:
        raise ValueError(f'"X-Hub-Signature" not supplied in header: {request.META}')

    result = False
    if hmac.compare_digest(github_signature, local_signature):
        result = True
    else:
        logger.error('webhook validation failed!')
        msg = f'github_signature({github_signature}) != local_signature({local_signature})'
        logger.debug(msg)
    return result


@csrf_exempt
def webhook(request: HttpRequest, organization_id: str):
    """
    Accepts the following github webhook events:

        - project_card
        - ping

    """
    logger.info('webhook request received')
    organization = get_object_or_404(KippoOrganization, pk=organization_id)

    try:
        is_validated = validate_webhook_request(request, organization)
    except ValueError as e:
        logger.exception(e)
        return HttpResponseBadRequest(*e.args)

    if not is_validated:
        return HttpResponseForbidden('Invalid "X-Hub-Signature"')

    if request.method == 'POST':
        # Github Webhook headers:
        # https://developer.github.com/webhooks/#delivery-headers
        #
        # Django converts incoming headers to a 'normalized' format, see:
        # https://docs.djangoproject.com/en/2.2/ref/request-response/#django.http.HttpRequest.META
        event_type = request.META.get('HTTP_X_GITHUB_EVENT', None)
        logger.debug(f'Processing event: X-Github-Event={event_type}')
        if not event_type:
            event_type = request.META.get('X-Github-Event', None)
        if event_type == 'project_card':
            logger.debug(f' -- decoding webhook event_type: {event_type}')
            unquoted_body = urllib.parse.unquote(request.body.decode('utf8'), encoding='utf8')
            parsed_body = unquoted_body.split('payload=')[-1]
            try:
                event = json.loads(parsed_body)
            except json.decoder.JSONDecodeError as e:
                logger.exception(e)
                logger.error(f'Unable to decode parsed_body: {parsed_body}')
                logger.error(f'Event cannot be processed: {event_type}')
                event = None
            if event:
                action = event['action']
                logger.debug(f' -- processing webhook event_type: {event_type}')
                logger.debug(f' -- event: {event}')
                try:
                    queue_incoming_project_card_event(organization, event_type, event)
                except KeyError as e:
                    logger.exception(e)
                    logger.warning(f'{event_type} action={event["action"]} missing expected key: {e.args}')
                assert action in ('created', 'edited', 'moved', 'converted', 'deleted')
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                if action == 'created':
                    status_code = HTTPStatus.CREATED
                elif action in ('edited', 'moved', 'converted', 'deleted'):
                    status_code = HTTPStatus.NO_CONTENT  # 204 - "resource updated successfully"
                return HttpResponse(status=status_code, content='201 Created')
            else:
                return HttpResponseBadRequest('json.decoder.JSONDecodeError -- unable to process payload')
        elif event_type == 'ping':
            return HttpResponse(status=HTTPStatus.OK, content='ping request validated')
        else:
            logger.warning(f'Unsupported event: {event_type}')
            return HttpResponseBadRequest(f'Unsupported event: {event_type}')
    return HttpResponseBadRequest('what are you talking about!?')
