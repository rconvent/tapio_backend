
import logging

from django.db import models
from django.utils.translation import gettext as _
from django_middleware_global_request import get_request
from project import mixin
from rest_framework.exceptions import ValidationError
from tapio.models.source import ModifiedSource, Source

logger = logging.getLogger(__name__)

class SourceLink(mixin.ModelSignals, models.Model):
    """    
    A link between a source (S) and an modified source (MS). A modication can alter a source 
    either by applying a ratio to the parent value or changing the emission_factor (EF) value.
    
    """    
    parent = models.ForeignKey(Source, on_delete=models.CASCADE, db_index=True, related_name="links")
    child = models.ForeignKey(ModifiedSource, on_delete=models.SET_NULL, null=True, db_index=True, related_name="link")

    ratio = models.FloatField(default=1, blank=True,  help_text=_("ratio to apply to the linked source"))    
    

    def __str__(self):
        return f"{self.parent.get_name()} <-> {self.child.get_name()} ({self.id})"

    def pre_save(self, *args, **kwargs):
        
        if self.parent.type!="S" :
            raise ValidationError({"parent" : _("Parent must be a source")})
        if self.child and self.child.type!="MS" :
            raise ValidationError({"child" : _("Child must be a modified source")})
        
        # only authorize on parent per child for now (as easy first implementation)
        if self.child and self.child.parents.count() > 0:
            raise ValidationError({"child" : _("Modified source can only be linked to one source")})
        
        pcompany = self.parent.company
        if self.child :
            ccompany = self.child.company

            # copy child source under parent source company
            if pcompany != ccompany  :
                copied_child = self.child
                copied_child.id = None 
                copied_child.save()

                self.child = copied_child
            


    def post_save(self, *args, **kwargs):
        # update child source 
        self.child.save()



