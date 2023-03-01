# python packages
import os
import sys

# sys.path.append('/home/root/project/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ["DOTENV_FILE"] = ".env"

import django
import django.conf as conf

django.setup()

from tapio.models import *

s  = Source.objects.first()
ms = ModifiedSource.objects.first()


