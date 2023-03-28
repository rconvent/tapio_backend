
import logging

from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext as _
from django_middleware_global_request import get_request
from project import mixin
from rest_framework.exceptions import PermissionDenied
from tapio.models.unit import Unit


class Source(mixin.ModelSignals, models.Model):
    """    
    An Emission is every source that generates GreenHouse gases (GHG).    
    It could be defined as source x emission_factor = total    
    """    
    
    names = models.JSONField(default=dict, editable=True, blank=True, help_text=_("names of this object in the form of a dictionnary, i.e. {'fr':'Nom', 'en':'Name'}"))
    company = models.ForeignKey(
        "Company", related_name="sources", null=False, on_delete=models.CASCADE, db_index=True, help_text="Company to which this source belong to"
    )
    description = models.CharField(max_length=250, blank=True, null=True)    
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=False, db_index=True, related_name="sources")
    
    value = models.FloatField(blank=True, null=True, help_text=_("quantity of source in Unit"))    
    emission_factor = models.FloatField(blank=True, null=True, help_text=_("emission of the source in Unit/kgCO2e"))    
    total_emission = models.FloatField(editable=False, blank=True, null=True, help_text=_("Total emission in kgCO2e"))     
    
    lifetime = models.PositiveIntegerField(blank=True, null=True)    
    acquisition_year = models.PositiveSmallIntegerField(blank=True, null=True)

    def get_total_emission(self, year=None):
        if not year or not self.acquisition_year :
            return self.total_emission
        else :
            if year < self.acquisition_year or year > self.acquisition_year + (self.lifetime or 0) :
                return 0
            else :
                return self.total_emission

    @property
    def get_name(self):
        return str(self.names.get("fr", next((name for name in self.names.values()), "NoName")))
    
    def __str__(self):
        return f"{self.get_name} ({self.id})"

    def pre_save(self, *args, **kwargs):
        
        if self.value and self.emission_factor :
            self.total_emission = self.value * self.emission_factor
        else :
            self.total_emission = None

        if self.total_emission and self.lifetime :
            self.total_emission /= self.lifetime
        

    def post_save(self, *args, **kwargs):
        # delete reduction strategies cached data
        for rs in self.reduction_stategies.all() :
            cache_key = f"reduction_strategy_{rs.pk}"
            cache.delete(cache_key)



