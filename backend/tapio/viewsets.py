from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from tapio.models import *
from tapio.serializers import *


class ReportViewSet(ModelViewSet):
    """    
    The Report is the sum of all the emissions. It should be done once a year    

    list:     Retrieve the list of reports.
    retrieve: Retrieve all information about a specific report.
    create:   Create a new report.
    delete:   Remove an existing report.
    update:   Update an report.
    """  
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]


class SourceViewSet(ModelViewSet):
    """    
    An Emission is every source that generates GreenHouse gases (GHG).    
    It could be defined as source x emission_factor = total  
     
    list:
        Retrieve the list of sources.

    retrieve:
        Retrieve all information about a specific source.

    create:
        Create a new source.

    delete:
        Remove an existing source.

    update:
        Update an source.
    """  
    
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    permission_classes = [IsAuthenticated]

class ModifiedSourceViewSet(ModelViewSet):
    """    
    An Emission is every source that generates GreenHouse gases (GHG).    
    It could be defined as source x emission_factor = total  
     
    list:
        Retrieve the list of sources.

    retrieve:
        Retrieve all information about a specific source.

    create:
        Create a new source.

    delete:
        Remove an existing source.

    update:
        Update an source.
    """  
    
    queryset = ModifiedSource.objects.all()
    serializer_class = ModifiedSourceSerializer
    permission_classes = [IsAuthenticated]


class ProfileViewSet(ModelViewSet):
    """    
    User profile 
     
    list:
        Retrieve the list of users.

    retrieve:
        Retrieve all information about a specific user.

    create:
        Create a new user.

    delete:
        Remove an existing company.

    update:
        Update an company.
    """  
    queryset = get_user_model().objects.all().select_related("auth_token", "profile")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class UnitViewSet(ModelViewSet):
    """    
    User profile 
     
    list:
        Retrieve the list of companies.

    retrieve:
        Retrieve all information about a specific company.

    create:
        Create a new company.

    delete:
        Remove an existing company.

    update:
        Update an company.
    """  
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class CompanyViewSet(ModelViewSet):
    """    
    Company Tree  
     
    list:
        Retrieve the list of companies.

    retrieve:
        Retrieve all information about a specific company.

    create:
        Create a new company.

    delete:
        Remove an existing company.

    update:
        Update an company.
    """  
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    