
from django.db import models
from django.utils.translation import gettext as _


class Unit(models.Model):
    """    
    Units     
    """ 
    name = models.CharField(max_length=128, unique=True)
    names = models.JSONField(default=dict, editable=True, blank=True, help_text=_("names of this object in the form of a dictionnary, i.e. {'fr':'Nom', 'en':'Name'}"))

    def __str__(self):
        return f"{self.name} ({self.id})"

    def pre_save(self, *args, **kwargs):
        pass

    def post_save(self, *args, **kwargs):
        pass





