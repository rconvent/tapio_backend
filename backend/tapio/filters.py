from django.db.models import F
from django.db.models.functions import Coalesce
from django_filters import CharFilter, DateFilter, FilterSet, NumberFilter
from tapio.models import *


class ReportFilter(FilterSet):

    date_from = DateFilter(field_name="date", lookup_expr='gte')
    date_to = DateFilter(field_name="date", lookup_expr='lte')
    year = NumberFilter(field_name="year")

    class Meta:
        model = Report
        fields = ['date_from', 'date_to']


class SourceFilter(FilterSet):

    def filter_queryset(self, queryset):    
        queryset = queryset.annotate(
            end_year=Coalesce(F("acquisition_year"),1900)+Coalesce(F("lifetime"), 0)
        )    
        return super().filter_queryset(queryset)
    
    acquisition_year_after = NumberFilter(field_name="acquisition_year",  lookup_expr='gte')
    end_year_befor = NumberFilter(field_name="end_year",  lookup_expr='lte')
    report_year = NumberFilter(field_name="report__year",  lookup_expr='lte')


    class Meta:
        model = Source
        fields = ['acquisition_year_after', 'end_year_befor', 'report_year']


