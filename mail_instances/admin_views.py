from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.contrib.contenttypes.models import ContentType

from .forms import get_message_form_class


def mail_instances_action(modeladmin, request, queryset):
    # display form
    # on submit save Message items
    # send emails
    ct = ContentType.objects.get_for_model(queryset.model)
    model_class = ct.model_class()
    form_class = get_message_form_class(model_class)
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    pks = ",".join(selected)
    initial = {
        'pks': pks,
        'ct': ct.pk,
    }

    form = form_class(initial=initial)
    context = {
        'form': form,
        'opts': model_class._meta,
    }
    template_name = 'admin/mail_instances/message_form.html'
    return TemplateResponse(request, template_name, context)

mail_instances_action.short_description = _('Send message to selected')
