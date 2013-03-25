from datetime import datetime
import logging

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string


class Message(models.Model):
    template = models.CharField(_('Template'), max_length=250)
    from_email = models.CharField(_('From'), max_length=200)
    subject = models.CharField(_('Subject'), max_length=200)
    body = models.TextField(_('Body'), blank=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True,
                                   blank=True, null=True)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['-created']

    def __unicode__(self):
        return self.subject


class Instance(models.Model):
    message = models.ForeignKey(Message, verbose_name=_('Message'))
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    obj = generic.GenericForeignKey('content_type', 'object_id')
    created = models.DateTimeField(default=datetime.now)
    is_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Message instance')
        verbose_name_plural = _('Message instances')

    def send_email(self):
        to = self.obj.get_recipients()
        raise Error
        ctx = {
            'message': self.message,
            'instance': self,
        }
        html_body = render_to_string(
            [self.message.template],
            ctx,
        )
        plain = strip_tags(html_body)
        msg = EmailMultiAlternatives(
            self.message.subject,
            plain,
            self.message.from_email,
            to=to,
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        self.is_sent = True
        self.save()
