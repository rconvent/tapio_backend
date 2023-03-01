
from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.utils.translation import gettext as _
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.
class Company(MPTTModel):
    """    
    Company Tree organisation. Orginased in tree so parent company can have access to the subsidiary reports 
    (and agregate them if they want it to)  
    """   

    name = models.CharField(max_length=256, db_index=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    tva_number = models.CharField(max_length=256, null=True, blank=True)
    phone_number = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.id})"

    def pre_save(self, *args, **kwargs):
        pass

    def post_save(self, *args, **kwargs):
        pass

