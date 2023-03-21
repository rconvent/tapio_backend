
import logging
from functools import reduce

from django.db import models
from django.utils.translation import gettext as _
from django_middleware_global_request import get_request
from project import mixin


class ReductionStrategy(mixin.ModelSignals, models.Model):
    """    
    A reduction strategy is a source (and associated modifiactions)    
    """    
    names = models.JSONField(
        default=dict, 
        editable=True, 
        blank=True, 
        help_text=_("names of this object in the form of a dictionnary, i.e. {'fr':'Nom', 'en':'Name'}")
    )
    source = models.ForeignKey(
        "Source", 
        on_delete=models.CASCADE, 
        null=False, 
        db_index=True, 
        related_name="reduction_stategies", 
        help_text="source of the strategy"
    )
    
    def get_total_emission(self, year=None):
        
        lifetime = self.source.lifetime or 0
        source_emission = self.source.get_total_emission(year=year)
        
        modifications = self.modifications.filter(effective_year__lte=year) if year else self.modifications.all()
        modifications = [m for m in modifications if not lifetime or (year or 0) <= (m.effective_year or 0) + lifetime]

        if not modifications:
            return source_emission
        
        # for modifications in series, we assume than ratio must be applied to the previous
        ratios = [m.ratio for m in modifications if m.ratio]
        ratio = reduce(lambda x, y: x * y, ratios) if ratios else 1

        # for modif is series we assume that the newest emission factor is always lower than previous modifications
        emission_factors = [m.emission_factor for m in modifications if m.emission_factor]
        emission_factor = min(emission_factors) if emission_factors else self.source.emission_factor

        modifications_emission = ratio * emission_factor * self.source.value
        if lifetime:
            modifications_emission /= lifetime
            return source_emission + modifications_emission

        return modifications_emission
    
    def get_delta(self, year=None):
        
        if self.source.get_total_emission(year=year) :
            return self.get_total_emission(year=year) - (self.source.total_emission or 0)

        return  self.get_total_emission(year=year)
        
        

    @property
    def get_name(self):
        return str(self.names.get("fr", next((name for name in self.names.values()), "NoName")))
    
    def __str__(self):
        return f"{self.get_name} ({self.id})"

    def pre_save(self, *args, **kwargs):
        pass
        
    def post_save(self, *args, **kwargs):
        pass



