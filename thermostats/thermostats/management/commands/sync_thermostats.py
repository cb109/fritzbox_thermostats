import logging
from pprint import pprint

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from pushover import Client
from pyfritzhome import Fritzhome

from thermostats.thermostats.models import Thermostat, ThermostatLog, WeekDay

TEMPERATURE_OFF = 126.5
TEMPERATURE_FALLBACK = 0

TIME_FORMAT = settings.TIME_INPUT_FORMATS[0]

logger = logging.getLogger("thermostats.sync")


def describe_temperature(temperature):
    if temperature == TEMPERATURE_OFF:
        return "off"
    return f"{temperature} °C"


def temperatures_equal(t1, t2):
    """Handle 'off' reported as 126.5, but must be set as 0."""
    if t1 == TEMPERATURE_OFF:
        t1 = 0
    if t2 == TEMPERATURE_OFF:
        t2 = 0
    return t1 == t2


def get_fritzbox_connection(
    host=settings.FRITZBOX_HOST,
    user=settings.FRITZBOX_USER,
    password=settings.FRITZBOX_PASSWORD,
):
    fritzbox = Fritzhome(host, user, password)
    fritzbox.login()
    return fritzbox


def get_fritzbox_thermostat_devices():
    fritzbox = get_fritzbox_connection()
    return [device for device in fritzbox.get_devices() if device.has_thermostat]


def send_push_notification(message, title=None):
    if not settings.PUSHOVER_USER_KEY or not settings.PUSHOVER_API_TOKEN:
        if title:
            logger.info(title)
        logger.info(message)
        return
    client = Client(settings.PUSHOVER_USER_KEY, api_token=settings.PUSHOVER_API_TOKEN)
    client.send_message(message, title=title)


def change_thermostat_target_temperature(
    thermostat, new_target_temperature, rule=None, notify=True
):
    ThermostatLog.objects.create(
        thermostat=thermostat,
        rule=rule,
        start_time=rule.start_time if rule else None,
        end_time=rule.end_time if rule else None,
        temperature=new_target_temperature,
    )

    # fritzbox = get_fritzbox_connection()
    # fritzbox.set_target_temperature(thermostat.ain, new_target_temperature)

    message = (
        f"{thermostat.name} is now set to "
        f"{describe_temperature(new_target_temperature)}"
    )
    if rule:
        message += f" by applying {rule}"
    else:
        message += f" by using the fallback"
    logger.warn(message)
    if notify:
        send_push_notification(
            message,
            title=(
                f"{thermostat.name} -> "
                f"{describe_temperature(new_target_temperature)}"
            ),
        )


class Command(BaseCommand):
    help = "Get and set thermostat temperatures based on rules"

    def handle(self, *args, **options):
        now = timezone.localtime()
        weekday = WeekDay.objects.get(order=now.weekday())
        logger.info(f"{weekday} {now.time().strftime(TIME_FORMAT)}")
        logger.info("")

        for device in get_fritzbox_thermostat_devices():
            thermostat = Thermostat.objects.get(ain=device.ain)

            # Update name to reflect changes from the fritzbox admin UI.
            if thermostat.name != device.name:
                logger.info(
                    f"Reflecting changed name {thermostat.name} -> {device.name}"
                )
                thermostat.name = device.name
                thermostat.save()

            # Check rules and compute a target temperature.
            last_matching_rule = None
            logger.info(
                f"{device.name} {describe_temperature(device.target_temperature)}"
            )
            for rule in thermostat.rules.all().order_by("start_time", "end_time"):
                if rule.is_valid_now():
                    last_matching_rule = rule
                    logger.info("  match: " + str(rule))
                else:
                    logger.info("  skip: " + str(rule))
            if last_matching_rule is None:
                logger.info("  no rule matched")
                if not temperatures_equal(
                    device.target_temperature, TEMPERATURE_FALLBACK
                ):
                    change_thermostat_target_temperature(
                        thermostat, TEMPERATURE_FALLBACK
                    )
            else:
                logger.info(f"  rule matched: {last_matching_rule}")
                if not temperatures_equal(
                    device.target_temperature, last_matching_rule.temperature
                ):
                    change_thermostat_target_temperature(
                        thermostat,
                        last_matching_rule.temperature,
                        rule=last_matching_rule,
                    )
            logger.info("")

            # TODO handle manual intervention by tracking temperatures
            #   and change-events; manual override should be valid until
            #   next scheduled change-event

            # TODO handle rules that only trigger and are not 'valid'
            #   over some timerange. need tracked events for this

            # TODO deploy on server with a cronjob every 5-10min,
            #   make sure the timezone is correct

            # TODO push updated temperature to device immediately when a
            #   rule has been added/changed/removed that affects it right
            #   now

            # TODO take a look at battery efficieny, communicate with
            #   thermostats only when needed

        # self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
