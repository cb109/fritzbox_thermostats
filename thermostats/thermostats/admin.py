from django.contrib import admin

from .models import Device, Rule, WeekDay


class WeekDayAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "order",
        "abbreviation",
        "is_weekend",
        "created_at",
        "id",
    )


class RuleAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "weekdays",
        "start_time",
        "end_time",
        "temperature",
        "created_at",
        "id",
    )

    def description(self, rule):
        return str(rule)

    def weekdays(self, rule):
        return rule.days_short_description


class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "ain",
        "rule_descriptions",
        "created_at",
        "id",
    )

    def rule_descriptions(self, device):
        rules = device.rules.all().order_by("id")
        return [str(rule) for rule in rules]


admin.site.site_header = "Thermostats"
admin.site.register(Device, DeviceAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(WeekDay, WeekDayAdmin)
