
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
        
        if self.source.total_emission is None or self.total_emission is None :
            return None
        # only return addition when year smaller than acqu. year + liftime else difference by default
        if year :
            # don't count modified source if report year less than aquisition (shouldn't append but idk...)
            if self.acquisition_year and self.acquisition_year > year:
                return 0
            elif year < (self.source.acquisition_year or 0) + (self.source.lifetime or 0) :
                return (self.source.total_emission + self.total_emission) - self.source.total_emission
            else :
                return self.total_emission - self.source.total_emission
        else : 
            return self.total_emission - self.source.total_emission
    

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
        # update source to update report (all this post save update can be done asyncronously with workers like celery)
        for report in  self.source.reports.all() :
            report.save()




