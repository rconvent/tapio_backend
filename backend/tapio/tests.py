from django.test import TestCase
from tapio.models import *

# Create your tests here.


class TapioTest(TestCase):
    
    fixtures = [
        "tapio/fixtures/companies.json",
        "tapio/fixtures/units.json",
        "tapio/fixtures/sources.json",
        "tapio/fixtures/modifiedSources.json",
    ]

    def testReport(self):
        print(Source.objects.values("names__fr", "modifiedSources__names__fr"))



