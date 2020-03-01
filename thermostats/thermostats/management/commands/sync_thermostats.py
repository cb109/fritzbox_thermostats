from pprint import pprint

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from pyfritzhome import Fritzhome

from thermostats.thermostats.models import Thermostat, WeekDay

TEMPERATURE_OFF = 126.5


def describe_temperature(temperature):
    if temperature == TEMPERATURE_OFF:
        return "off"
    return f"{temperature} °C"


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


class Command(BaseCommand):
    help = "Get and set thermostat temperatures based on rules"

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        now = timezone.localtime()
        weekday = WeekDay.objects.get(order=now.weekday())
        print(weekday, now.time().strftime("%H:%M"))
        print()

        for device in get_fritzbox_thermostat_devices():
            thermostat = Thermostat.objects.get(ain=device.ain)

            # Update name to reflect changes from the fritzbox admin UI.
            if thermostat.name != device.name:
                thermostat.name = device.name
                thermostat.save()

            # Check rules and compute a target temperature.
            last_matching_rule = None
            print(device.name, describe_temperature(device.target_temperature))
            for rule in thermostat.rules.all().order_by("start_time", "end_time"):
                if rule.is_valid_now():
                    last_matching_rule = rule
                    print("  match: " + str(rule))
                else:
                    print("  skip: " + str(rule))
            if last_matching_rule is None:
                print("  no rule matched")
            print()

            # TODO order rules by start_time, but filter rules for the current time
            #   then pass each, last wins to set temp, apply if current target_temp
            #   differs

            # TODO push notifications about change events and errors,
            #   also track stuff with an extra log model

            # TODO handle rules that only trigger and are not 'valid'
            #   over some timerange. need tracked events for this

            # TODO handle manual intervention by tracking temperatures
            #   and change-events; manual override should be valid until
            #   next scheduled change-event

            # TODO deploy on server with a cronjob every 5-10min,
            #   make sure the timezone is correct

        # self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
