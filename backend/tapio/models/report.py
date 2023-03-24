from collections import defaultdict

from django.db import models
from django.utils.translation import gettext as _
from project import mixin
from rest_framework.exceptions import ValidationError


# Create your models here.
class Report(mixin.ModelSignals, models.Model):
    """    
    The Report is the sum of all the emissions. It should be done once a year. Can be done for a company
    and their subsidaries.    
    """   
    names = models.JSONField(default=dict, editable=True, blank=True, help_text=_("names of this object in the form of a dictionnary, i.e. {'fr':'Nom', 'en':'Name'}"))
    date = models.DateField()
    year =  models.PositiveSmallIntegerField(blank=True, null=True, help_text=_("Carbon footprint report year"))
    deltas = models.JSONField(
        default=dict, 
        editable=False, 
        blank=False, 
        help_text=_("delta and total emission by scenarios {'1' : {'initial' = 100, 'modified' = 50, 'delta'= 50}, '2' : {...} ")
    )

    @property
    def get_name(self):
        return str(self.names.get("fr", next((name for name in self.names.values()), "NoName")))

    def __str__(self):
        return f"{self.get_name} ({self.id})"

    def pre_save(self, *args, **kwargs):
        
        #computed different scenario deltas 
        self.deltas = defaultdict(lambda: defaultdict(int))
        for entry in self.report_entries.all(): 
            
            self.deltas[entry.scenario]["modified"] += entry.total_emission
            self.deltas[entry.scenario]["delta"] += entry.delta
            self.deltas[entry.scenario]["initial"] += entry.total_emission - entry.delta
                
        
    def post_save(self, *args, **kwargs):
        pass

