import collections

from django_utils import view_decorators

from . import forms


@view_decorators.env
def index(request):
    data = request.POST or None

    request.context['form'] = forms.TagsInputForm(data)
