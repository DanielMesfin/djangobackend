from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Tuple

from django.contrib import admin
from django.utils import timezone


class BaseDateRangeFilter(admin.SimpleListFilter):
    template = "admin/filters/date_range.html"

    # To be set by factory
    title: str = "Date range"
    parameter_name: str = "date"
    field_path: str = ""

    @property
    def start_param(self) -> str:
        return f"{self.parameter_name}_start"

    @property
    def end_param(self) -> str:
        return f"{self.parameter_name}_end"

    def lookups(self, request, model_admin):
        return ()

    def choices(self, changelist):
        # Use default implementation but with our template rendering values
        return []

    def queryset(self, request, queryset):
        start_raw = request.GET.get(self.start_param)
        end_raw = request.GET.get(self.end_param)

        start_dt: Optional[datetime] = None
        end_dt: Optional[datetime] = None

        if start_raw:
            try:
                start_dt = datetime.strptime(start_raw, "%Y-%m-%d")
                start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
            except Exception:
                start_dt = None
        if end_raw:
            try:
                end_dt = datetime.strptime(end_raw, "%Y-%m-%d") + timedelta(days=1)
                end_dt = timezone.make_aware(end_dt, timezone.get_current_timezone())
            except Exception:
                end_dt = None

        if start_dt is not None:
            queryset = queryset.filter(**{f"{self.field_path}__gte": start_dt})
        if end_dt is not None:
            queryset = queryset.filter(**{f"{self.field_path}__lt": end_dt})
        return queryset


def make_date_range_filter(field_path: str, *, title: Optional[str] = None, parameter_name: Optional[str] = None):
    class _ConcreteDateRangeFilter(BaseDateRangeFilter):
        pass

    _ConcreteDateRangeFilter.field_path = field_path
    _ConcreteDateRangeFilter.title = title or "Date range"
    _ConcreteDateRangeFilter.parameter_name = (parameter_name or field_path).replace("__", "_")
    _ConcreteDateRangeFilter.__name__ = f"DateRangeFilter_{field_path.replace('__', '_')}"
    return _ConcreteDateRangeFilter
