from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from tapio.filters import *
from tapio.models import *
from tapio.serializers import *


class ReportViewSet(ModelViewSet):
    """    
    The Report is the sum of all the emissions. It should be done once a year    

    list:     Retrieve the list of reports.</br>
    retrieve: Retrieve all information about a specific report.</br>
    create:   Create a new report.</br>
    delete:   Remove an existing report.</br>
    update:   Update an report.</br>
    """  
    queryset = Report.objects.all().prefetch_related("sources")
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ReportFilter
    search_fields = ["names"]



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
    
    queryset = Source.objects.all().prefetch_related("modifiedSources")
    serializer_class = SourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SourceFilter
    search_fields = ["names"]

class ModifiedSourceViewSet(ModelViewSet):
    """    
    An Emission is every source that generates GreenHouse gases (GHG).    
    It could be defined as source x emission_factor = total  
     
    list:     Retrieve the list of sources.</br>
    retrieve: Retrieve all information about a specific source.</br>
    create:   Create a new source.</br>
    delete:   Remove an existing source.</br>
    update:   Update an source.</br>
    """  
    
    queryset = ModifiedSource.objects.all()
    serializer_class = ModifiedSourceSerializer
    permission_classes = [IsAuthenticated]


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

    