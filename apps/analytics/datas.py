import os
import django
import json

from asgiref.sync import sync_to_async
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.core.serializers import serialize

from apps.analytics.models import AnalysisData


