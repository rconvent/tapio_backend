from collections import defaultdict

from django.contrib.auth import get_user_model
from django.db.models import F, FloatField, Func, Sum, Value
from django.db.models.functions import Cast, Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from tapio.filters import *
from tapio.models import *
from tapio.serializers import *


class ReportViewSet(ModelViewSet):
    """    
    The Report is the sum of all the emissions. It should be done once a year    

    list:     Retrieve the list of reports. User ?full=true to access all informations and not a summary</br>
    retrieve: Retrieve all information about a specific report.</br>
    create:   Create a new report.</br>
    delete:   Remove an existing report.</br>
    update:   Update an report.</br>
    """  
    queryset = Report.objects.all().prefetch_related("report_entries")
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ReportFilter
    search_fields = ["names"]

    @extend_schema(
        parameters=[
            OpenApiParameter("start_year", OpenApiTypes.INT),
            OpenApiParameter("end_year", OpenApiTypes.INT),
            OpenApiParameter("scenario", OpenApiTypes.STR),
        ]
    )
    @action(methods=["get"], detail=False, url_path="years_emission")
    def get_years_emission(self, request, *args, **kwargs):
        
        start_year = request.query_params.get("start_year", 2999)
        end_year = request.query_params.get("end_year", 1900)
        scenario = request.query_params.get("scenario", 1900)

        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(year__gte=start_year, year__lte=end_year)
        queryset = queryset.annotate(
            source_emissions = Coalesce(
                Cast(
                    Func(F(f"deltas"), Value(scenario), Value("initial"), function="jsonb_extract_path_text"),
                    FloatField(),
                ),   
                0.0
            )
        )
        emissions = defaultdict(int)
        for item in queryset.values("date__year", "source_emissions"):
            emissions[item.get("date__year", 0)] += item.get("source_emissions")
        
        return Response(emissions)

class ReductionStrategyViewSet(ModelViewSet):
    """    
    An Emission is every source that generates GreenHouse gases (GHG).    
    It could be defined as source x emission_factor = total  
     
    list:     Retrieve the list of sources.</br>
    retrieve: Retrieve all information about a specific source.</br>
    create:   Create a new source.</br>
    delete:   Remove an existing source.</br>
    update:   Update an source.</br>
    """  
    
    queryset = ReportEntry.objects.all().prefetch_related("source", "modified_source")
    serializer_class = ReportEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"full": self.request.GET.get("full", False)})

        # get report year to computed delta on modified source (not for list view)
        if context.get("view", object).__dict__.get("action", None) not in ("list", "create") :
            context.update({"year": self.get_object().report.year})
        return context


class SourceViewSet(ModelViewSet):
    """    
    An Emission is every source that generates GreenHouse gases (GHG).    
    It could be defined as source x emission_factor = total  
     
    list:     Retrieve the list of sources.</br>
    retrieve: Retrieve all information about a specific source.</br>
    create:   Create a new source.</br>
    delete:   Remove an existing source.</br>
    update:   Update an source.</br>
    """  
    
    queryset = Source.objects.all().prefetch_related("modifications")
    serializer_class = SourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SourceFilter
    search_fields = ["names"]


    @action(methods=["get"], detail=False, url_path="years_emission")
    def get_years_emission(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())
        print(queryset.count())
        queryset = queryset.annotate(
            source_emissions = Coalesce(F("total_emission"), 0.0)
        )

        items_list = list(queryset.values("acquisition_year", "lifetime", "total_emission"))
        date_from = request.query_params.get("acquisition_year_after", 0)
        date_to = request.query_params.get("end_year_befor", 2999)
        
        emissions= {}
        for year in range(int(date_from), int(date_to)+1):
            emissions[year] = sum(
                item.get("total_emission", 0) for item in items_list  if item.get("acquisition_year", 0) <= year <=item.get("acquisition_year", 2999)+(item.get("lifetime") or 0)
            )
        
        return Response(emissions)
    

class ProfileViewSet(ModelViewSet):
    """    
    User profile 
     
    list      Retrieve the list of users.</br>
    retrieve: Retrieve all information about a specific user.</br>
    create:   Create a new user.</br>
    delete:   Remove an existing company.</br>
    update:   Update an company.</br>
    """  
    queryset = get_user_model().objects.all().select_related("auth_token", "profile")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class UnitViewSet(ModelViewSet):
    """    
    User profile 
     
    list:     Retrieve the list of companies.</br>
    retrieve: Retrieve all information about a specific company.</br>
    create:   Create a new company.</br>
    delete:   Remove an existing company.</br>
    update:   Update an company.</br>
    """  
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

class CompanyViewSet(ModelViewSet):
    """    
    Company Tree  
     
    list:     Retrieve the list of companies.</br>
    retrieve: Retrieve all information about a specific company.</br>
    create:   Create a new company.</br>
    delete:   Remove an existing company.</br>
    update:   Update an company.</br>
    """  
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    