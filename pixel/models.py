from django.contrib.postgres import fields
from django.db import models


class PageViewModel(models.Model):
    history_uuid = models.UUIDField()
    session_uuid = models.UUIDField()

    domain = models.CharField(max_length=120)
    url = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    time_spent = models.FloatField(default=0)
    ip = models.CharField(max_length=20, null=True)
    referrer = models.CharField(max_length=120)
    headers = fields.JSONField(null=True)
    params = fields.JSONField(null=True)
    query = fields.JSONField(null=True)

    @property
    def user(self):
        try:
            return UserModel.objects.get(history_uuid=self.history_uuid).email
        except:
            return None


class UserModel(models.Model):
    email = models.CharField(max_length=120)
    history_uuid = models.UUIDField()

    class Meta:
        unique_together = ('email', 'history_uuid')

    @property
    def pageviews(self):
        return list(PageViewModel.objects.filter(history_uuid=self.history_uuid))

    @property
    def sessions(self):
        return list(PageViewModel.objects.values_list('session_uuid', flat=True)\
            .filter(history_uuid=self.history_uuid).distinct())
