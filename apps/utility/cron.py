import os
import datetime
import logging

from django.db.models import Q
from django.conf import settings


def send_reminder():
    now = datetime.datetime.now()
    print("Running Timing:", now.strftime("%Y-%m-%d %H:%M:%S"))