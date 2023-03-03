from collections import defaultdict

import rest_registration.api.serializers as registration_serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from tapio.models import *


class DefaultLoginSerializer(registration_serializers.DefaultLoginSerializer):
    # also support getting the login as "username" or "email" for backward compatibility
    def to_internal_value(self, data):
        if data.get("login", None) is None and data.get("username", None) is not None:
            data["login"] = data.pop("username", None)

        if data.get("login", None) is None and data.get("email", None) is not None:
            data["login"] = data.pop("email", None)

        # make it lower case
        data["login"] = data["login"].lower()

        return super().to_internal_value(data)

class TokenSerializer(serializers.Serializer):
    token = serializers.SerializerMethodField()

    def get_token(self, obj) -> str:
        token, _ = Token.objects.get_or_create(user=obj)
        return token.key
    
    
class UserProfileSerializer(ModelSerializer):
    
    class Meta:
        model = UserProfile
        fields = ["company", "language"]


class UserSerializer(ModelSerializer):
    
    profile = UserProfileSerializer(
        many=False, read_only=False, required=False, allow_null=False
    )
   
    class Meta:
        model = get_user_model()
        fields = ["username", "profile"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        profile.company = profile_data.get('company', profile.company)
        profile.language = profile_data.get('language', profile.language)
        profile.save()

        return instance

class CompanySerializer(ModelSerializer):
    
    class Meta:
        model = Company
        fields = ["id", "name"]


class UnitSerializer(ModelSerializer):

    class Meta:
        model = Unit
        fields = '__all__'


class ModifiedSourceSerializer(ModelSerializer):

    id = serializers.IntegerField(read_only=False, allow_null=True, default=None)
    delta = serializers.SerializerMethodField(required=False)
    @extend_schema_field(serializers.JSONField(read_only=False, allow_null=True, required=False))
    def get_delta(self, obj) -> dict:
        return obj.get_delta()

    class Meta:
        model = ModifiedSource
        fields =[
            "id",
            "names",
            "ratio",
            "emission_factor",
            "total_emission",
            "acquisition_year",
            "delta"
        ]

class SourceSerializer(ModelSerializer):
    
    def create(self, validated_data):
        modified_sources_data = validated_data.pop('modifiedSources', [])
        source = Source.objects.create(**validated_data)
        
        # create modified source if not existing else only link to source)
        for ms_data in modified_sources_data:
            if not ms_data.get("id") :
                ms = ModifiedSource.objects.create(source=source, **ms_data)
            else :
                ms = ModifiedSource.objects.get(id=ms_data.get("id"))
                if ms.source :
                    raise ValidationError({"Modified Source" : f"Modified Source {ms.id} has already a linked source"})
                ms.source = source
                ms.save()

        return source
    
    def update(self, instance, validated_data):
        modified_sources_data = validated_data.pop('modifiedSources', [])
        
        # create modified source if not existing else only link to source
        ids_list = []
        for ms_data in modified_sources_data:
            if not ms_data.get("id") :
                ms = ModifiedSource.objects.create(source=instance, **ms_data)
                ids_list += [ms.id]
            else :
                ms = ModifiedSource.objects.get(id=ms_data.get("id"))
                if ms.source.id!=instance.id :
                    raise ValidationError({"Modified Source" : f"Modified Source {ms.id} has another a linked source"})
                ms.save()
                ids_list += [ms.id]
        
        # delete unlinked modified source
        ModifiedSource.objects.filter(source=instance).exclude(id__in=ids_list).delete()
        instance.save()

        return instance


    id = serializers.IntegerField(read_only=False, allow_null=True, default=None)
    modifiedSources = ModifiedSourceSerializer(many=True, read_only=False, required=False, allow_null=False)

    class Meta:
        model = Source
        fields = [
            "id",
            "names",
            "company",
            "value",
            "emission_factor",
            "total_emission",
            "lifetime",
            "acquisition_year",
            "modifiedSources"
        ]



class ReportSerializer(ModelSerializer):
    def to_representation (self, instance):
        data = super().to_representation(instance)
        if self.context.get("full", False):
            return data

        scenarios = data.pop("scenarios", {})
        sources_list = data.pop("sources", [])

        filled_scenarios = defaultdict(list)
        for scenario, sources in scenarios.items() :
            for source in sources :
                s_id = source.get("scenario_id")
                ms_id = source.get("modified_scenario_id")
                
                s = [e for e in sources_list if e.get("id")==s_id]
                if s :
                    s = s[0]
                    ms = s.pop("modifiedSources", [])
                    ms = [e for e in ms if e.get("id")==ms_id]
                    s["modifiedSource"] = ms[0] if ms else {}
                    filled_scenarios[scenario] += [s] 
        data["scenarios"] = filled_scenarios
        
        return data
    
    def create(self, validated_data):
        sources_data = validated_data.pop('sources', [])
        report = Report.objects.create(**validated_data)
        
        for s_data in sources_data:
            if not s_data.get("id") :
                s = Source.objects.create(**s_data)
            else :
                s = Source.objects.get(id=s_data.get("id"))
            report.sources.add(s)
        
        return report
    
    def update(self, instance, validated_data):
        sources_data = validated_data.pop('sources', [])
        instance.names = validated_data.get("names")
        instance.scenarios = validated_data.get("scenarios")
        
        instance.sources.clear()
        for s_data in sources_data:
            if not s_data.get("id"):
                s = Source.objects.create(**s_data)
            else :
                s = Source.objects.get(id=s_data.get("id"))    
            instance.sources.add(s)
    
        instance.save()

        return instance
    
    sources = SourceSerializer(many=True, read_only=False, required=False, allow_null=False)
    
    class Meta:
        model = Report
        fields = [
            "id",
            "names", 
            "date",
            "year",
            "scenarios",
            "sources"
        ]


        