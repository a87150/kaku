from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone

from notifications.views import AllNotificationsList
from actstream.signals import action

from .models import Picture, Address


class IndexView(ListView):

    paginate_by = 20
    model = Picture
    template_name = "picture/index.html"
    context_object_name = "picture_list"

    def get_queryset(self):
        return Picture.objects.order_by("-created_time")