from django.conf.urls import url, patterns
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from .models import Message, Instance
from .forms import get_message_form_class


class InstanceInline(admin.TabularInline):
    model = Instance
    extra = 0
    fields = ['obj', 'created', 'is_sent']
    readonly_fields = ['obj', 'created', 'is_sent']


class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created',)
    readonly_fields = ('subject', 'from_email', 'created', 'html_body')
    date_hierarchy = 'created'
    search_fields = ['subject']
    inlines = [
        InstanceInline
    ]

    def html_body(self, obj):
        return mark_safe(obj.body)
    html_body.is_safe = True

    def get_urls(self):
        urls = super(MessageAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^mail_instances/$',
                               self.admin_site.admin_view(self.mail_instances),
                               name='mail_instances_message_mail_instances'),
                           )
        return my_urls + urls

    def mail_instances(self, request, *args, **kwargs):
        ct = ContentType.objects.get(pk=request.POST['ct'])
        model_class = ct.model_class()
        form_class = get_message_form_class(model_class)
        form = form_class(request.POST)
        if form.is_valid():
            message = form.save()
            cleaned_data = form.cleaned_data
            pks = cleaned_data['pks'].split(',')
            instances = ct.model_class().objects.filter(pk__in=pks)
            for instance in instances:
                message.instance_set.create(obj=instance)

            errors = []
            for instance in message.instance_set.all():
                try:
                    instance.send_email()
                except Exception, e:
                    errors.append(repr(e))

            if errors:
                message = _('Some errors occured. Please review message.')
                messages.warning(request, message)
            else:
                message = _('Sending finished')
                messages.success(request, message)

            opts = ct.model_class()._meta
            url = reverse('admin:%s_%s_changelist' %
                          (opts.app_label, opts.module_name),
                          current_app=self.admin_site.name)
            return HttpResponseRedirect(url)
        else:
            template_name = 'admin/mail_instances/message_form.html'
            context = {
                'form': form,
                'opts': model_class._meta,
            }
            return TemplateResponse(request, template_name, context)


admin.site.register(Message, MessageAdmin)
