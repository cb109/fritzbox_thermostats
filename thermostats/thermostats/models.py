from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(default=timezone.now)


class WeekDay(BaseModel):
    name = models.CharField(max_length=32)
    order = models.IntegerField()
    is_weekend = models.BooleanField(default=False)

    @property
    def abbreviation(self):
        return self.name[:2]

    def __str__(self):
        return f"{self.name}"


class Rule(BaseModel):
    name = models.CharField(default="", max_length=128)
    days = models.ManyToManyField("thermostats.WeekDay", blank=True)
    start_time = models.TimeField(blank=True)
    end_time = models.TimeField(blank=True)
    temperature = models.IntegerField(default=21)

    @property
    def days_short_description(self):
        return ", ".join([day.abbreviation for day in self.days.all()])

    def __str__(self):
        return f"{self.name} ({self.days_short_description})"


class Device(BaseModel):
    ain = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    rules = models.ManyToManyField("thermostats.Rule", blank=True)

    def __str__(self):
        return f"{self.name} (AIN: '{self.ain}')"
