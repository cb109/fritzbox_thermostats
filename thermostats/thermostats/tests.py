import os
from datetime import time

import pytest
from django.conf import settings
from django.core.management import call_command
from freezegun import freeze_time
from model_bakery import baker

from thermostats.thermostats.models import WeekDay


@pytest.fixture(autouse=True)
def default_weekdays(db):
    for name, order in (
        ("Monday", 0),
        ("Tuesday", 1),
        ("Wednesday", 2),
        ("Thursday", 3),
        ("Friday", 4),
        ("Saturday", 5),
        ("Sunday", 6),
    ):
        baker.make("thermostats.WeekDay", name=name, order=order)


@pytest.fixture
def all_weekdays(db):
    return WeekDay.objects.all()


class TestRuleIsValidNow:
    @freeze_time("19:30")
    def test_too_early(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(20, 0),
            end_time=time(22, 0),
        )
        assert not rule.is_valid_now()

    @freeze_time("19:30")
    def test_in_between_normal_range(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(16, 0),
            end_time=time(22, 0),
        )
        assert rule.is_valid_now()

    @freeze_time("19:30")
    def test_in_between_wrapping_range(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(22),
            end_time=time(6, 0),
        )
        assert rule.is_valid_now()

    @freeze_time("19:30")
    def test_too_late(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(16, 0),
            end_time=time(18, 0),
        )
        assert not rule.is_valid_now()

    @freeze_time("19:30")
    def test_early_start_no_end(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule", weekdays=all_weekdays, start_time=time(16, 0),
        )
        assert rule.is_valid_now()

    @freeze_time("19:30")
    def test_late_start_no_end(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule", weekdays=all_weekdays, start_time=time(21, 0),
        )
        assert not rule.is_valid_now()
