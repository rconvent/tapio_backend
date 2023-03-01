
import logging

from django.db import models
from django.utils.translation import gettext as _
from django_middleware_global_request import get_request
from project import mixin
from rest_framework.exceptions import PermissionDenied
from tapio.models.company import Company
from tapio.models.unit import Unit


def pprint(*args, **kwargs):
    # print("\n\n")
    return print("\n\nDEBUG", *args, end="\n\n", **kwargs)

class Source(mixin.ModelSignals, models.Model):
    """    
    An Emission is every source that generates GreenHouse gases (GHG).    
    It could be defined as source x emission_factor = total    
    """    
    
    names = models.JSONField(default=dict, editable=True, blank=True, help_text=_("names of this object in the form of a dictionnary, i.e. {'fr':'Nom', 'en':'Name'}"))
    company = models.ForeignKey(
        Company, related_name="sources", null=False, on_delete=models.CASCADE, db_index=True, help_text="Company to which this source belong to"
    )
    description = models.CharField(max_length=250, blank=True, null=True)    
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=False, db_index=True, related_name="sources")
    
    value = models.FloatField(blank=True, null=True, help_text=_("quantity of source in Unit"))    
    emission_factor = models.FloatField(blank=True, null=True, help_text=_("emission of the source in Unit/kgCO2e"))    
    total_emission = models.FloatField(editable=False, blank=True, null=True, help_text=_("Total emission in kgCO2e"))     
    
    lifetime = models.PositiveIntegerField(blank=True, null=True)    
    acquisition_year = models.PositiveSmallIntegerField(blank=True, null=True)

    @property
    def get_name(self):
        return str(self.names.get("fr", next((name for name in self.names.values()), "NoName")))
    
    def __str__(self):
        return f"{self.get_name} ({self.id})"

    def pre_save(self, *args, **kwargs):
        
        request = get_request()
        # verify that user have rigths 
        if request:
            company_id =  request.user.company_id
            if company_id != self.company.id and company_id not in Company.objects.get(id=company_id).get_descendants().values_list("id", flat=True):
                raise PermissionDenied({"company": _("must be below user company")}, code="invalid")
        
        if self.value and self.emission_factor :
            self.total_emission = self.value * self.emission_factor
        else :
            self.total_emission = None

        if self.total_emission and self.lifetime :
            self.total_emission /= self.lifetime
        

    def post_save(self, *args, **kwargs):
        # update linked modified source (all this post save update can be done with asyncronously tasks using workers like celery)
        for modifiedSource in self.modifiedSources.all() :
            modifiedSource.save()



