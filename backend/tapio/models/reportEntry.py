
import logging

from django.db import models
from django.utils.translation import gettext as _
from django_middleware_global_request import get_request
from project import mixin


class ReportEntry(mixin.ModelSignals, models.Model):
    """    
    A report entry is a reduction_strategy in a scenario of a report.   
    """    

    reduction_strategy = models.ForeignKey("ReductionStrategy", on_delete=models.SET_NULL, null=True, db_index=True, related_name="report_entries", help_text="modfied source of this entry")
    report = models.ForeignKey("Report", on_delete=models.CASCADE, null=False, db_index=True, related_name="report_entries", help_text="Report link sof this entry")
    scenario = models.CharField(default="00", max_length=10, editable=True, help_text="scenario of this entry : 01, 02, ...")
    delta = models.FloatField(
        default=0, 
        editable=False, 
        blank=False, 
        help_text=_("delta for this report entry")
    )
    total_emission = models.FloatField(
        default=0, 
        editable=False, 
        blank=False, 
        help_text=_("total emission for this report entry")
    )

    class Meta:
        unique_together = ('reduction_strategy', 'scenario', 'report')
        
    
    def __str__(self):
        return f"{self.report.get_name} - {self.reduction_strategy.get_name if self.reduction_strategy else None}"

    def pre_save(self, *args, **kwargs):
        
        if self.reduction_strategy :
            source_data = self.reduction_strategy.source_data
            self.total_emission = self.reduction_strategy.get_total_emission(year=self.report.year) 
            
            if self.reduction_strategy.get_source_total_emission(source_data, year=self.report.year) :
                self.delta = self.total_emission - (source_data.get("total_emission") or 0)
            else :  
                self.delta = self.total_emission

    def post_save(self, *args, **kwargs):
        pass



