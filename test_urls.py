# -*- coding: utf-8 -*-
from __future__ import absolute_import
from functools import partial
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms import Form
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect
from django.template.response import TemplateResponse
from django.contrib.auth import urls as auth_urls
from django.utils.datetime_safe import datetime


def returns_redirect(request, permanent):
    return redirect('/', permanent=permanent)


returns_permanent_redirect = partial(returns_redirect, permanent=True)


def returns_render(request):
    return render(request, template_name="admin/base.html", context={})


def returns_render_to_response(request):
    return render_to_response(template_name="admin/base.html", context={})


def returns_templateresponse(request):
    return TemplateResponse(request, template="admin/base.html", context={
        'form': Form(),
        # 'queryset': get_user_model().objects.all(),
        'model': get_user_model()(),
        'thing': 1,
        'dt': datetime.today(),
        'sub': {
            'sub2': {
                'yay': 1,
                'woo': 'heh',
            }
        }
    })


def returns_jsonresponse(request):
    from django.http import JsonResponse
    return JsonResponse(data={
        'lol': 1,
    })


@login_required
def index(request):
    urls = {
        'templateresponse': reverse('1'),
        'jsonresponse': reverse('2'),
        'render': reverse('3'),
        'render_response': reverse('4'),
        'redirect_permanent': reverse('5'),
        'redirect': reverse('6'),
    }
    return HttpResponse(content='''<!doctype html>
    <html><body>
    <ul>
        <li><a href="{urls[templateresponse]}">Template Response</a></li>
        <li><a href="{urls[jsonresponse]}">JSON Response</a></li>
        <li><a href="{urls[render]}?a=1&b=2&a=3">Render shortcut</a></li>
        <li><a href="{urls[render_response]}">Render to Response shortcut</a></li>
        <li><a href="{urls[redirect_permanent]}">301 Redirect</a></li>
        <li><a href="{urls[redirect]}">302 Redirect</a></li>
    </ul>
    </body></html>'''.format(urls=urls))


urlpatterns = [
    url(r'^accounts/', include(auth_urls)),
    url(r'^$', index, name='index'),
    url(r'^1/$', returns_templateresponse, name='1'),
    url(r'^2/$', returns_jsonresponse, name='2'),
    url(r'^3/$', returns_render, name='3'),
    url(r'^4/$', returns_render_to_response, name='4'),
    url(r'^5/$', returns_permanent_redirect, name='5'),
    url(r'^6/$', returns_redirect, kwargs={'permanent': False}, name='6'),
    url(r'^admin/', include(admin.site.urls)),
]
