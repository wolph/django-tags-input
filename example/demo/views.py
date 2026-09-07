from typing import Any

from django_utils import view_decorators

from . import forms


@view_decorators.env
def index(request: Any) -> None:
    request.template = 'index.html'
    data: Any = request.POST or None

    request.context['form'] = forms.TagsInputForm(data)
