from django.db.models import F
from django.db.models.functions import Coalesce
from django_filters import (
    BooleanFilter,
    CharFilter,
    DateFilter,
    Filter,
    FilterSet,
    NumberFilter,
)
from tapio.models import *


class ListFilterIds(Filter):
    def filter(self, qs, value):
        if value not in (None, ''):
            integers = [int(v) for v in value.split(',')]
            return qs.filter(**{'%s__%s' % (self.field_name, self.lookup_expr): integers})
        return qs
    
class ReportFilter(FilterSet):

    date_from = DateFilter(field_name="date", lookup_expr='gte')
    date_to = DateFilter(field_name="date", lookup_expr='lte')
    year = NumberFilter(field_name="year")

    class Meta:
        model = Report
        fields = ['date_from', 'date_to']

class ReportEntryFilter(FilterSet):
    
    # reduction_strategy = NumberFilter(field_name="reduction_strategy", lookup_expr='exact')
    # report = NumberFilter(field_name="report_id", lookup_expr='exact')
    # scenario = CharFilter(field_name="scenario", lookup_expr='exact')

    class Meta:
        model = ReportEntry
        fields = ['reduction_strategy', 'report_id', 'scenario']


class SourceFilter(FilterSet):

    def filter_queryset(self, queryset):    
        queryset = queryset.annotate(
            end_year=Coalesce(F("acquisition_year"), 1900)+Coalesce(F("lifetime"), 0)
        )    
        return super().filter_queryset(queryset)
    
    ids = NumberFilter(field_name="id", lookup_expr='in')
    acquisition_year_before = NumberFilter(field_name="acquisition_year",  lookup_expr='lte')
    end_year_after = NumberFilter(field_name="end_year",  lookup_expr='gte')
    no_year = BooleanFilter(field_name="acquisition_year", lookup_expr="isnull")
    ids=ListFilterIds(field_name="id", lookup_expr='in')


    class Meta:
        model = Source
        fields = ['acquisition_year_before', 'end_year_after', 'no_year']

