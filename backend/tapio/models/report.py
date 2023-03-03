
from django.db import models
from django.utils.translation import gettext as _
from tapio.models import Source


# Create your models here.
class Report(models.Model):
    """    
    The Report is the sum of all the emissions. It should be done once a year. Can be done for a compan
    and their subsidaries.    
    """   
    names = models.JSONField(default=dict, editable=True, blank=True, help_text=_("names of this object in the form of a dictionnary, i.e. {'fr':'Nom', 'en':'Name'}"))
    date = models.DateField()
    sources = models.ManyToManyField(Source, blank=True, related_name="reports")    
    scenarios = models.JSONField(
        default=dict, 
        editable=True, 
        blank=False, 
        help_text=_("list of modified sources per scenario {scenario_1 : [{'s_id1' : 'ms_id1'}, ..], scenario_2 : [{'s_id1' : 'ms_id2'}, ..]}")
    )


    def get_name(self):
        return str(self.names.get("fr", next((name for name in self.names.values()), "NoName")))

    def __str__(self):
        return f"{self.get_name()} ({self.id})"

    def pre_save(self, *args, **kwargs):
        pass

    def post_save(self, *args, **kwargs):
        pass

