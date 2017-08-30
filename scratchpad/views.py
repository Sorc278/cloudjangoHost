# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import Note

# Create your views here.
def show_notes(request):
    context = {
        'notes': Note.objects.order_by('-date'),
    }
    return render(request, 'scratchpad/index.html', context)