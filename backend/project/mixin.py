class ModelSignals(object):
    """A Model mixin class that lets you put your signal handler methods back into your Model class."""

    @classmethod
    def _sig_pre_init(cls, instance, *args, **kwargs):
        """dispatch the pre_init method to a regular instance method."""
        if not hasattr(instance, "skip_pre_init"):
            instance.pre_init(*args, **kwargs)

    @classmethod
    def _sig_post_init(cls, instance, *args, **kwargs):
        """dispatch the post_init method to a regular instance method."""
        if not hasattr(instance, "skip_post_init"):
            instance.post_init(*args, **kwargs)

    @classmethod
    def _sig_pre_delete(cls, instance, *args, **kwargs):
        """dispatch the pre_delete method to a regular instance method."""
        if not hasattr(instance, "skip_pre_delete"):
            instance.pre_delete(*args, **kwargs)

    @classmethod
    def _sig_post_delete(cls, instance, *args, **kwargs):
        """dispatch the post_delete method to a regular instance method."""
        if not hasattr(instance, "skip_post_delete"):
            if hasattr(cls, "post_delete"):
                instance.post_delete(*args, **kwargs)

    @classmethod
    def _sig_pre_save(cls, instance, *args, **kwargs):
        """dispatch the pre_save method to a regular instance method."""
        if instance.pk is None:
            instance._created = True
            if hasattr(instance, "pre_create") and not hasattr(instance, "skip_pre_create"):
                instance.pre_create()

        # only run presave if the object has an id
        if (instance.pk or getattr(instance, "skip_resave", False)) and not hasattr(instance, "skip_pre_save"):
            if hasattr(instance, "pre_save"):
                instance.pre_save(*args, **kwargs)

    @classmethod
    def _sig_post_save(cls, instance, *args, **kwargs):
        """dispatch the post_save method to a regular instance method."""

        created = kwargs.get("created", False)
        if created:
            if hasattr(instance, "post_create") and not hasattr(instance, "skip_post_create"):
                instance.post_create()

            if not getattr(instance, "skip_resave", False):
                instance.save()  # resave the model to trigger pre_save

            if hasattr(instance, "_created"):
                delattr(instance, "_created")

        if (not created or getattr(instance, "skip_resave", False)) and not hasattr(instance, "skip_post_save"):
            if hasattr(cls, "post_save"):
                instance.post_save(*args, **kwargs)


    @classmethod
    def connect(cls):
        """Connect a django signal with this model."""
        from django.db.models.signals import (
            post_delete,
            post_init,
            post_save,
            pre_delete,
            pre_init,
            pre_save,
        )

        # List all signals you want to connect with here:
        if hasattr(cls, "pre_init"):
            pre_init.connect(cls._sig_pre_init, sender=cls)
        if hasattr(cls, "post_init"):
            post_init.connect(cls._sig_post_init, sender=cls)
        if hasattr(cls, "pre_delete"):
            pre_delete.connect(cls._sig_pre_delete, sender=cls)
        if hasattr(cls, "post_delete") :
            post_delete.connect(cls._sig_post_delete, sender=cls)
        if hasattr(cls, "pre_save") or hasattr(cls, "pre_create"):
            pre_save.connect(cls._sig_pre_save, sender=cls)
        if (
            hasattr(cls, "post_save")
            or hasattr(cls, "post_create")
        ):
            post_save.connect(cls._sig_post_save, sender=cls)
