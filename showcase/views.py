"""Native page backed by the same dispatcher as the browser demo."""

from __future__ import annotations

import json
import logging
from typing import Any

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from tags_input.widgets import TagsInputWidgetBase

from .forms import FORMS
from .runtime import dispatch_json

logger: logging.Logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    """Render and submit the native showcase form."""
    mode: str = request.GET.get('mode', 'create')
    payload: dict[str, str] = {
        'mode': mode,
        'action': 'save' if request.method == 'POST' else 'load',
    }
    if request.method == 'POST':
        field_name: str = 'contacts' if mode == 'composite' else 'tags'
        values: list[str] = TagsInputWidgetBase().value_from_datadict(
            request.POST, request.FILES, field_name
        )
        payload['values'] = request.POST.get('values', ','.join(values))
    try:
        state: dict[str, Any] = json.loads(dispatch_json(json.dumps(payload)))
    except ValueError as exc:
        # Log the reason server-side. The response stays generic so exception
        # text never reaches the client.
        logger.warning('Rejected showcase request: %s', exc)
        return HttpResponseBadRequest('Invalid showcase request.')
    state['media'] = FORMS[mode]().media
    return render(request, 'showcase/index.html', state)
