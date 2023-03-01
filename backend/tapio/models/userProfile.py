
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DefaultUserManager
from django.db import models
from project import mixin
from tapio.models.company import Company

langChoices = [
    ('fr', 'french'),
    ('en', 'english'),
    ('nl', 'dutch'),
]

class UserManager(DefaultUserManager):
    """Define a model manager for User model with no username field."""

    # overwrite get_queryset to always add select_related
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related("profile", "profile__company")
        return qs



class User(mixin.ModelSignals, AbstractUser):
    signal_redux = True
    signal_redis = False

    class Meta:
        db_table = "auth_user"

    objects = UserManager()

    def pre_save(self, *args, **kwargs):
        self.username = self.username.lower()

    def post_save(self, *args, **kwargs):

        if getattr(self, "_created", False):
            profile, created = UserProfile.objects.get_or_create(user=self)
            

    @property
    def company_id(self):
        return self.profile.company_id

    @property
    def company(self):
        return self.profile.company
    
class UserProfile(models.Model):
    """
    User profile : company of the user and is pref language
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE, related_name="profile")
    company = models.ForeignKey(Company, related_name="users", null=True, on_delete=models.CASCADE)
    language = models.CharField(null=False, default="fr", max_length=2, choices=langChoices, db_index=True)

