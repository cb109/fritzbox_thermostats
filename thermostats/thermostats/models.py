from datetime import datetime, time, timedelta

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

    def _get_valid_timeframes(self):
        left = self.start_time
        right = self.end_time if self.end_time else END_OF_DAY

        valid_timeframes = [(left, right)]
        if right < left:
            valid_timeframes = [
                (left, END_OF_DAY),
                (START_OF_DAY, right),
            ]
        return valid_timeframes

    def is_valid_now(self):
        """Whether this Rule is in effect right now.

        Checks for assigned weekdays and current time. If no end_time is
        specified, the implicit end_time is midnight.

        """
        now = datetime.now()
        now_time = now.time()

        if not now.weekday() in self.weekdays.values_list("order", flat=True):
            return False

        valid_timeframes = self._get_valid_timeframes()
        for left, right in valid_timeframes:
            left_ok = left <= now_time
            right_ok = right >= now_time
            if left_ok and right_ok:
                return True
        return False

    def has_been_triggered_within_timeframe_already(self):
        last_log = self.logs.last()
        if last_log is None:
            return False

        rule_has_changed = (
            last_log.start_time != self.start_time
            or last_log.end_time != self.end_time
            or last_log.temperature != self.temperature
        )
        if rule_has_changed:
            return False

        now = datetime.now()
        now_time = now.time()

        today = now.date()
        yesterday = today - timedelta(days=1)

        last_log_time = last_log.created_at.time()
        timeframes = self._get_valid_timeframes()

        if len(timeframes) == 1:
            timeframe_today = timeframes[0]
            today_left, today_right = timeframe_today
            if today_left <= last_log_time and today_right >= last_log_time:
                if last_log.created_at.date() == today:
                    return True

        elif len(timeframes) == 2:
            timeframe_yesterday, timeframe_today = timeframes

            yesterday_left, yesterday_right = timeframe_yesterday
            if yesterday_left <= last_log_time and yesterday_right >= last_log_time:
                if last_log.created_at.date() == yesterday:
                    return True

            today_left, today_right = timeframe_today
            if today_left <= last_log_time and today_right >= last_log_time:
                if last_log.created_at.date() == today:
                    return True

        return False


class Thermostat(BaseModel):
    ain = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    rules = models.ManyToManyField("thermostats.Rule", blank=True)

    def __str__(self):
        return f"{self.name} (AIN: '{self.ain}')"


class ThermostatLog(BaseModel):
    thermostat = models.ForeignKey(
        "thermostats.Thermostat", related_name="logs", on_delete=models.CASCADE
    )
    rule = models.ForeignKey(
        "thermostats.Rule", null=True, related_name="logs", on_delete=models.CASCADE
    )
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    temperature = models.FloatField()

    def __str__(self):
        return f"{self.thermostat}: {self.rule}"
