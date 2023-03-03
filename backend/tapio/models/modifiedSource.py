
import logging

from django.db import models
from django.utils.translation import gettext as _
from django_middleware_global_request import get_request
from project import mixin
from tapio.models.source import Source


class ModifiedSource(mixin.ModelSignals, models.Model):
    """    
    A modifed Source is simply a source with herited value from the original (or modified)
    """    
    
    source  = models.ForeignKey(Source, on_delete=models.CASCADE, db_index=True, related_name="modifiedSources")    
    names = models.JSONField(default=dict, editable=True, blank=True, help_text=_("names of this object in the form of a dictionnary, i.e. {'fr':'Nom', 'en':'Name'}"))
    
    description = models.CharField(max_length=250, blank=True, null=True)    
    
    ratio = models.FloatField(blank=True, default=1, help_text=_("Ratio to apply to the original source"))   
    emission_factor = models.FloatField(blank=True, null=True, help_text=_("local emission of the modified source (if different than origianl) in Unit/kgCO2e"))
    total_emission = models.FloatField(editable=False, blank=True, null=True, help_text=_("Total emission in kgCO2e"))     
    
    acquisition_year = models.PositiveSmallIntegerField(blank=True, null=True)

    @property
    def get_name(self):
        return str(self.names.get("fr", next((name for name in self.names.values()), "NoName")))
    
    def get_delta(self, year=None):
        
        if not self.source.total_emission or not self.total_emission :
            return None
        
        # if no lifetime simply return differnce
        if not self.source.lifetime :
            return self.source.total_emission - self.total_emission

        # if lifetime check if source is amortized. if not add source emission
        if (year or 0) < (self.source.acquisition_year or 0 + self.source.lifetime) :
            return self.source.total_emission + self.total_emission
        
        if (self.source.acquisition_year or 0 + self.source.lifetime) < (year or 2999)  :
            return self.source.total_emission - self.total_emission
        
        return None

    @property
    def delta(self):
        return self.get_delta(self)


    def __str__(self):
        return f"{self.get_name} ({self.id})"

    def pre_save(self, *args, **kwargs):
        # TODO : prefetch related 

        if self.source.value is None :
            self.total_emission = None
        elif self.emission_factor is not None :
            self.total_emission = self.ratio * self.emission_factor * self.source.value
        else :
            self.total_emission = self.ratio * self.source.emission_factor * self.source.value if  self.source.emission_factor else None

        # make assumption than modified source has same liftime
        if self.total_emission and self.source.lifetime :
            self.total_emission /= self.source.lifetime

    def post_save(self, *args, **kwargs):
        # update report of linked source (all this post save update can be done asyncronously with workers like celery)
        for report in self.source.reports.all():
            report.save()




