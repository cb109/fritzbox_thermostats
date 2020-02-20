from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(default=timezone.now)


class WeekDay(BaseModel):
    name = models.CharField(max_length=32)
    order = models.IntegerField()

    @property
    def abbreviation(self):
        return self.name[:2]

    def __str__(self):
        return f"{self.name}"


class Rule(BaseModel):
    name = models.CharField(default="", max_length=128)
    weekdays = models.ManyToManyField("thermostats.WeekDay", blank=True)
    start_time = models.TimeField(blank=True)
    end_time = models.TimeField(blank=True, null=True)
    temperature = models.IntegerField(default=21)

    def is_valid_now(self, now=None):
        """Whether this Rule is in effect right now.

        Checks for assigned weekdays and current time. If no end_time is
        specified, the implicit end_time is midnight.

        """
        if now is None:
            now = timezone.now()
        now_time = now.time()

        if not now.weekday() in self.weekdays.values_list("order", flat=True):
            return False

        left = self.start_time
        right = self.end_time
        if self.end_time is not None and self.end_time < self.start_time:
            left = self.end_time
            right = self.start_time

        if now_time < left:
            return False
        if right:
            return now_time <= right
        return True

    @property
    def weekdays_short_description(self):
        return ", ".join([day.abbreviation for day in self.weekdays.all()])

    def __str__(self):
        return f"{self.name} ({self.weekdays_short_description})"


class Thermostat(BaseModel):
    ain = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    rules = models.ManyToManyField("thermostats.Rule", blank=True)

    def __str__(self):
        return f"{self.name} (AIN: '{self.ain}')"
