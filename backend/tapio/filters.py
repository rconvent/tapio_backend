from django_filters import DateFilter, FilterSet
from tapio.models import *


class ReportFilter(FilterSet):

    date_from = DateFilter(field_name="date", lookup_expr='gte')
    date_to = DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        model = Report
        fields = ['date_from', 'date_to']


class SourceFilter(FilterSet):
    
    date_from = DateFilter(field_name="reports__date", lookup_expr='gte')
    date_to = DateFilter(field_name="reports__date", lookup_expr='lte')

    class Meta:
        model = Source
        fields = ['date_from', 'date_to']