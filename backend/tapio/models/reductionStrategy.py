
import logging
from functools import reduce

from django.core.cache import cache
from django.db import models
from django.db.models import Prefetch, prefetch_related_objects
from django.utils.translation import gettext as _
from django_middleware_global_request import get_request
from project import mixin
from tapio.models import Modification


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

    def get_cache_key(self):
        return f"reduction_strategy_{self.pk}"
    

    @property
    def modifications_data(self):
        # check if data is in cache
        cache_key = self.get_cache_key()
        modifications_data = cache.get(cache_key, {}).get("modifications", None)
        
        if modifications_data is None:
            # fetch data from db and store in cache
            modifications_data = list(self.modifications.values("effective_year", "ratio", "emission_factor"))
            cache.set(cache_key, {**cache.get(cache_key, {}), "modifications" : modifications_data})

        return modifications_data
    
    @property
    def source_data(self):
        # check if data is in cache
        cache_key = self.get_cache_key()
        source_data = cache.get(cache_key, {}).get("source", None)
        
        if source_data is None:
            # fetch data from db and store in cache
            source_data = {
                "lifetime" : self.source.lifetime, 
                "value":self.source.value, 
                "emission_factor":self.source.emission_factor, 
                "total_emission": self.source.total_emission, 
                "acquisition_year": self.source.acquisition_year, 
            }
            cache.set(cache_key, {**cache.get(cache_key, {}), "source" : source_data})
        return source_data
    

    def get_source_total_emission(self, source_data, year=None):
        if not year or not source_data.get("acquisition_year") :
            return source_data.get("total_emission")
        else :
            if year < source_data.get("acquisition_year") or year > source_data.get("acquisition_year") + (source_data.get("lifetime")or 0) :
                return 0
            else :
                return source_data.get("total_emission")
            
            
    def get_total_emission(self, year=None):
        
        source_data = self.source_data
        lifetime = self.source_data.get("lifetime") or 0
        source_emission = self.get_source_total_emission(source_data, year=year)
        
        modifications = self.modifications_data
        if year :
            modifications = [m for m in modifications if m.get("effective_year", 2999) <= year] 
        modifications = [m for m in modifications if not lifetime or (year or 0) <= (m.get("effective_year") or 0) + lifetime]

        if not modifications:
            return source_emission
        
        # for modifications in series, we assume than ratio must be applied to the previous
        ratios = [m.get("ratio", 1) for m in modifications]
        ratio = reduce(lambda x, y: x * y, ratios) if ratios else 1

        # for modif is series we assume that the newest emission factor is always lower than previous modifications
        emission_factors = [m.get("emission_factor") for m in modifications if m.get("emission_factor")]
        emission_factor = min(emission_factors) if emission_factors else self.source_data.get("emission_factor", 0)

        modifications_emission = ratio * emission_factor * source_data.get("value",0)
        if lifetime:
            modifications_emission /= lifetime
            return source_emission + modifications_emission

        return modifications_emission
    
    def get_delta(self, year=None):
        source_data = self.source_data
        if self.get_source_total_emission(source_data, year=year) :
            return self.get_total_emission(year=year) - (source_data.get("total_emission") or 0)

        return  self.get_total_emission(year=year)
        
        

    @property
    def get_name(self):
        return str(self.names.get("fr", next((name for name in self.names.values()), "NoName")))
    
    def __str__(self):
        return f"{self.get_name} ({self.id})"

    def pre_save(self, *args, **kwargs):
        cache_key = self.get_cache_key()
        cache.delete(cache_key)
        
    def post_save(self, *args, **kwargs):
        pass



