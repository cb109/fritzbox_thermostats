from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Rule, Thermostat, WeekDay


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
        list_tags = "".join([f"<li>{rule}</li>" for rule in rules])
        html = f"<ul>{list_tags}</ul>"
        return html


admin.site.site_header = "Thermostats"
admin.site.register(Thermostat, ThermostatAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(WeekDay, WeekDayAdmin)
