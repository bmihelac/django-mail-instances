from django import forms
from django.conf import settings
from django.utils.importlib import import_module

from .models import Message


class MessageForm(forms.ModelForm):
    pks = forms.CharField(widget=forms.HiddenInput)
    ct = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Message


def default_get_message_form_class(model_class):
    return MessageForm


class_path = getattr(
    settings,
    'MAIL_INSTANCES_MESSAGE_FORM_CLASS',
    'mail_instances.forms.default_get_message_form_class'
)
class_module, class_name = class_path.rsplit('.', 1)
mod = import_module(class_module)
get_message_form_class = getattr(mod, class_name)
