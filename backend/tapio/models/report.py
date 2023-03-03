from collections import defaultdict

from django.db import models
from django.utils.translation import gettext as _
from project import mixin
from rest_framework.exceptions import ValidationError
from tapio.models import Source


# Create your models here.
class Report(mixin.ModelSignals, models.Model):
    """    
    The Report is the sum of all the emissions. It should be done once a year. Can be done for a compan
    and their subsidaries.    
    """   
    names = models.JSONField(default=dict, editable=True, blank=True, help_text=_("names of this object in the form of a dictionnary, i.e. {'fr':'Nom', 'en':'Name'}"))
    date = models.DateField()
    year =  models.PositiveSmallIntegerField(blank=True, null=True, help_text=_("Carbon footprint report year"))
    sources = models.ManyToManyField(Source, blank=True, related_name="reports")    
    scenarios = models.JSONField(
        default=dict, 
        editable=True, 
        blank=False, 
        help_text=_("list of modified sources per scenario {scenario_1 : [{'s_id1' : 'ms_id1'}, ..], scenario_2 : [{'s_id1' : 'ms_id2'}, ..]}")
    )

    @property
    def scenario_delta(self):
        #computed different scenario deltas 
        scenario_delta = defaultdict(lambda: defaultdict(int))
        for scenario, sources in self.scenarios.items():
            for source in sources :

                s = self.sources.filter(id=source.get("scenario_id")).first()
                ms = s.modifiedSources.filter(id=source.get("modified_scenario_id")).first()
                if s and ms :
                    scenario_delta[scenario]["itinial"] += s.total_emission
                    scenario_delta[scenario]["modified"] += s.total_emission + ms.get_delta(year=self.year)
                    scenario_delta[scenario]["delta"] += ms.get_delta(year=self.year)
                
        return scenario_delta

    def get_name(self):
        return str(self.names.get("fr", next((name for name in self.names.values()), "NoName")))

    def __str__(self):
        return f"{self.get_name()} ({self.id})"

    def pre_save(self, *args, **kwargs):
        pass
        
    def post_save(self, *args, **kwargs):
        pass

