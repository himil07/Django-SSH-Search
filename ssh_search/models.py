from django.db import models

class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

class SiteUser(TimeStampedModel):
    # Primary Key
    _id = models.BigAutoField(primary_key=True)

    # Unique Key
    email = models.CharField(max_length=255, unique=True, null=False, blank=False)

    # Other
    first_name = models.CharField(max_length=255, null=False, blank=False)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=False, blank=False)
    session_id = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.email


class SocialLogin(TimeStampedModel):
    # Primary Key
    _id = models.BigAutoField(primary_key=True)

    # Foreign Key
    user = models.ForeignKey('SiteUser', on_delete=models.CASCADE, null=True ,to_field='email')

    # Other
    auth_token = models.CharField(max_length=64, null=True, blank=True)
    site_name = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        ordering = ['user_id']
