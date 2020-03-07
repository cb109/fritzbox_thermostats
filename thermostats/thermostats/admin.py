from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Rule, Thermostat, ThermostatLog, WeekDay


class WeekDayAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "abbreviation",
        "created_at",
        "id",
    )
    ordering = ("order",)


class RuleAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "enabled",
        "week_days",
        "start_time",
        "end_time",
        "temperature",
        "created_at",
        "id",
    )
    ordering = (
        "start_time",
        "end_time",
    )

    def description(self, rule):
        return str(rule)

    def week_days(self, rule):
        return rule.weekdays_short_description


class ThermostatLogAdmin(admin.ModelAdmin):
    list_display = (
        "thermostat",
        "rule",
        "start_time",
        "end_time",
        "temperature",
        "created_at",
        "id",
    )
    ordering = ("-created_at",)


class ThermostatAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "ain",
        "rule_descriptions",
        "created_at",
        "id",
    )
    ordering = ("id",)

    @mark_safe
    def rule_descriptions(self, thermostat):
        rules = thermostat.rules.all().order_by("start_time", "end_time")
        list_tags = []
        for rule in rules:
            tag = "<li"
            if not rule.enabled:
                tag += ' style="color: lightgrey"'
            tag += f">{rule}</li>"
            list_tags.append(tag)
        html = f"<ul>{''.join(list_tags)}</ul>"
        return html


admin.site.site_header = "Thermostats"
admin.site.register(Rule, RuleAdmin)
admin.site.register(Thermostat, ThermostatAdmin)
admin.site.register(ThermostatLog, ThermostatLogAdmin)
admin.site.register(WeekDay, WeekDayAdmin)
