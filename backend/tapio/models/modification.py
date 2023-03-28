
import logging

from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext as _
from django_middleware_global_request import get_request
from project import mixin


class Modification(mixin.ModelSignals, models.Model):
    """    
    A modifed Source is simply a source with herited value from the original (or modified)
    """    

    # could M2M (but as you try to not use them, I used M2O)
    reduction_strategy = models.ForeignKey("ReductionStrategy", on_delete=models.CASCADE, null=False, related_name="modifications", help_text="linked reduction strategy of the modification")

    ratio = models.FloatField(blank=True, default=1, help_text=_("Ratio to apply to the source"))   
    emission_factor = models.FloatField(blank=True, null=True, help_text=_("Modified emission factor for the source")) 
    effective_year = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f"Ratio : {self.ratio}, EF : {self.emission_factor}"

    def pre_save(self, *args, **kwargs):
        pass

    def post_save(self, *args, **kwargs):
        # delete reduction strategies cached data
        cache_key = f"reduction_strategy_{self.reduction_strategy.pk}"
        cache.delete(cache_key)





