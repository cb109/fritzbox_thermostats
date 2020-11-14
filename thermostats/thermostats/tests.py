import logging
import os
from datetime import datetime, time, timedelta

import pytest
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

from freezegun import freeze_time
from model_bakery import baker
from thermostats.thermostats.models import Thermostat, WeekDay

logger = logging.getLogger("thermostats.tests")


@pytest.fixture(autouse=True)
def utc_timezone(monkeypatch):
    monkeypatch.setattr("django.conf.settings.TIME_ZONE", "UTC")


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

    @freeze_time("23:30")
    def test_in_between_wrapping_range_1(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(22),
            end_time=time(6, 0),
        )
        assert rule.is_valid_now()

    @freeze_time("12:15")
    def test_in_between_wrapping_range_2(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(19, 0),
            end_time=time(10, 0),
        )
        assert not rule.is_valid_now()

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
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(16, 0),
        )
        assert rule.is_valid_now()

    @freeze_time("19:30")
    def test_late_start_no_end(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(21, 0),
        )
        assert not rule.is_valid_now()


class TestRuleHasBeenTriggeredWithinTimeframeAlready:
    @freeze_time("16:30")
    def test_in_between_timeframe(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(16, 0),
            end_time=time(22, 0),
        )
        thermostat = baker.make("thermostats.Thermostat", rules=[rule])
        assert rule.is_valid_now()
        assert not rule.has_been_triggered_within_timeframe_already()

        thermostatlog = baker.make(
            "thermostats.ThermostatLog",
            thermostat=thermostat,
            rule=rule,
            start_time=rule.start_time,
            end_time=rule.end_time,
            temperature=rule.temperature,
        )
        thermostatlog.created_at = timezone.now() - timedelta(minutes=28)
        thermostatlog.save()

        assert rule.is_valid_now()
        assert rule.has_been_triggered_within_timeframe_already()

    @freeze_time("23:30")
    def test_after_timeframe(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(16, 0),
            end_time=time(22, 0),
        )
        thermostat = baker.make("thermostats.Thermostat", rules=[rule])
        assert not rule.is_valid_now()
        assert not rule.has_been_triggered_within_timeframe_already()

        thermostatlog = baker.make(
            "thermostats.ThermostatLog",
            thermostat=thermostat,
            rule=rule,
            start_time=rule.start_time,
            end_time=rule.end_time,
            temperature=rule.temperature,
        )
        thermostatlog.created_at = timezone.now()
        thermostatlog.save()

        assert not rule.is_valid_now()
        assert not rule.has_been_triggered_within_timeframe_already()

    @freeze_time("09:00")
    def test_wrapping_timeframe(self, all_weekdays):
        rule = baker.make(
            "thermostats.Rule",
            weekdays=all_weekdays,
            start_time=time(19, 0),
            end_time=time(10, 0),
        )
        thermostat = baker.make("thermostats.Thermostat", rules=[rule])
        assert rule.is_valid_now()
        assert not rule.has_been_triggered_within_timeframe_already()

        thermostatlog = baker.make(
            "thermostats.ThermostatLog",
            thermostat=thermostat,
            rule=rule,
            start_time=rule.start_time,
            end_time=rule.end_time,
            temperature=rule.temperature,
        )
        thermostatlog.created_at = timezone.now() - timedelta(days=1)
        thermostatlog.created_at = thermostatlog.created_at.replace(hour=23, minute=0)
        thermostatlog.save()

        assert rule.is_valid_now()
        assert rule.has_been_triggered_within_timeframe_already()


def test_thermostatlog_is_fallback(db):
    thermostatlog = baker.make("thermostats.ThermostatLog")
    assert not thermostatlog.is_fallback

    thermostatlog = baker.make(
        "thermostats.ThermostatLog",
        rule=None,
        start_time=None,
        end_time=None,
        temperature=22,
    )
    assert not thermostatlog.is_fallback

    thermostatlog = baker.make(
        "thermostats.ThermostatLog",
        rule=None,
        start_time=None,
        end_time=None,
        temperature=settings.TEMPERATURE_FALLBACK,
    )
    assert thermostatlog.is_fallback


class MockedFritzbox:
    def login(*args, **kwargs):
        pass

    def set_target_temperature(*args, **kwargs):
        pass

    def get_devices(*args, **kwargs):
        pass


class MockedDevice:
    def __init__(self, ain, name, target_temperature):
        self.ain = ain
        self.name = name
        self.target_temperature = target_temperature
        self.has_thermostat = True


def mocked_send_push_notification(message, title=None):
    logger.debug(title)
    logger.debug(message)


def test_names_synced_and_new_device_created_automatically(db, monkeypatch):
    # Setup
    device_livingroom = MockedDevice("11962 0785015", "Living Room", 21)
    device_kitchen = MockedDevice("11962 0785016", "Kitchen", 21)

    thermostat_livingroom = baker.make(
        "thermostats.Thermostat", ain=device_livingroom.ain, name="Other name"
    )
    assert Thermostat.objects.count() == 1
    assert thermostat_livingroom.name != device_livingroom.name

    def mocked_get_fritzbox_connection():
        return MockedFritzbox()

    def mocked_get_fritzbox_thermostat_devices():
        return [
            device_livingroom,
            device_kitchen,
        ]

    monkeypatch.setattr(
        (
            "thermostats.thermostats.management.commands."
            "sync_thermostats.send_push_notification"
        ),
        mocked_send_push_notification,
    )
    monkeypatch.setattr(
        (
            "thermostats.thermostats.management.commands."
            "sync_thermostats.get_fritzbox_connection"
        ),
        mocked_get_fritzbox_connection,
    )
    monkeypatch.setattr(
        (
            "thermostats.thermostats.management.commands."
            "sync_thermostats.get_fritzbox_thermostat_devices"
        ),
        mocked_get_fritzbox_thermostat_devices,
    )

    # Test
    call_command("sync_thermostats")

    assert Thermostat.objects.count() == 2
    thermostat_livingroom.refresh_from_db()
    assert thermostat_livingroom.name == device_livingroom.name

    thermostat_kitchen = Thermostat.objects.last()
    assert thermostat_kitchen.ain == device_kitchen.ain
    assert thermostat_kitchen.name == device_kitchen.name
