from datetime import time

import pytz
from django.conf import settings
from django.db import models
from django.utils import timezone

START_OF_DAY = time(0, 0)
END_OF_DAY = time(23, 59, 59, 999)


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
    temperature = models.FloatField(default=21.0)

    def is_valid_now(self, now=None):
        """Whether this Rule is in effect right now.

        Checks for assigned weekdays and current time. If no end_time is
        specified, the implicit end_time is midnight.

        """
        current_tz = pytz.timezone(settings.TIME_ZONE)
        if now is None:
            now = timezone.localtime()
        now_time = current_tz.localize(now.time())

        if not now.weekday() in self.weekdays.values_list("order", flat=True):
            return False

        left = current_tz.localize(self.start_time)
        right = current_tz.localize(self.end_time or END_OF_DAY)

        valid_timeframes = [(left, right)]
        if right < left:
            valid_timeframes = [
                (left, current_tz.localize(END_OF_DAY)),
                (current_tz.localize(START_OF_DAY), right),
            ]

        for left, right in valid_timeframes:
            left_ok = left <= now_time
            right_ok = right >= now_time
            if left_ok and right_ok:
                return True
        return False

    @property
    def weekdays_short_description(self):
        return ", ".join([day.abbreviation for day in self.weekdays.all()])

    def __str__(self):
        timing = f"{self.start_time.strftime('%H:%M')}"
        if self.end_time is not None:
            timing += f" - {self.end_time.strftime('%H:%M')}"
        return (
            f"{self.name}, ({self.weekdays_short_description}), "
            f"{timing}: {int(self.temperature)} °C"
        )


class Thermostat(BaseModel):
    ain = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    rules = models.ManyToManyField("thermostats.Rule", blank=True)

    def __str__(self):
        return f"{self.name} (AIN: '{self.ain}')"


class ThermostatLog(BaseModel):
    thermostat = models.ForeignKey("thermostats.Thermostat", on_delete=models.CASCADE)
    rule = models.ForeignKey("thermostats.Rule", null=True, on_delete=models.CASCADE)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    temperature = models.FloatField()

    def __str__(self):
        return f"{self.thermostat}: {self.rule}"
