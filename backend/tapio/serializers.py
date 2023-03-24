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


class ModificationSerializer(ModelSerializer):

    id = serializers.IntegerField(read_only=False, allow_null=True, default=None)

    class Meta:
        model = Modification
        fields =[
            "id",
            "ratio",
            "emission_factor",
            "effective_year",
        ]

class SourceSerializer(ModelSerializer):
    
    id = serializers.IntegerField(read_only=False, allow_null=True, default=None)

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
        ]

class ReductionStrategySerializer(ModelSerializer):
    
    def create(self, validated_data):
        
        source_data = validated_data.pop('source')
        modifications_data = validated_data.pop('modifications', [])
        
        # create source if not existing
        if not source_data.get("id") :
            source = Source.objects.create(**source_data)
        else :
            source = Source.objects.get(id=source_data.get("id"))
        reduction_strategy = ReductionStrategy.objects.create(**validated_data, source=source)

        # create each modification 
        for modif_data in modifications_data:
            Modification.objects.create(reduction_strategy=reduction_strategy, **modif_data)

        reduction_strategy.save()

        return reduction_strategy
    
    def update(self, instance, validated_data):
        
        modifications_data = validated_data.pop('modifications', [])
        instance.names = validated_data.get("names")

        # create modifications if not
        ids_list = []
        for modif_data in modifications_data:
            if not modif_data.get("id") :
                modification = Modification.objects.create(reduction_strategy=instance, **modif_data)
                ids_list += [modification.id]
            else :
                modification = Modification.objects.get(id=modif_data.get("id"))
                # copy modifications if already linked to another reduction strategy
                if modification.reduction_strategy.id!=instance.id :
                    modification.id = None
                    modification.reduction_strategy = instance
                    modification.save()
                ids_list += [modification.id]
        
        # delete unlinked modified source
        Modification.objects.filter(reduction_strategy=instance).exclude(id__in=ids_list).delete()
        instance.save()

        return instance

    id = serializers.IntegerField(read_only=False, allow_null=True, default=None)
    source = SourceSerializer(read_only=False, required=True, allow_null=False)
    modifications = ModificationSerializer(many=True, read_only=False, required=False, allow_null=False)
    delta = serializers.SerializerMethodField(required=False)
    total_emission = serializers.SerializerMethodField(required=False)
    
    @extend_schema_field(serializers.JSONField(read_only=True, allow_null=True, required=False))
    def get_delta(self, obj) -> dict:
        year = self.context.get("year", None)
        if year :
            year = int(year)
        return obj.get_delta(year=year)
    
    @extend_schema_field(serializers.JSONField(read_only=True, allow_null=True, required=False))
    def get_total_emission(self, obj) -> dict:
        year = self.context.get("year", None)
        if year :
            year = int(year)
        return obj.get_total_emission(year=year)
    
    class Meta:
        model = ReductionStrategy
        fields = [
            "id",
            "names",
            "source",
            "modifications",
            "delta",
            "total_emission"
        ]


class ReportEntrySerializer(ModelSerializer):
    
    id = serializers.IntegerField(read_only=False, allow_null=True, default=None)
    reduction_strategy_id = serializers.IntegerField(read_only=False, allow_null=True, default=None)
    
    class Meta:
        model = ReportEntry
        fields = [
            "id",
            "reduction_strategy_id",
            "scenario",
            "delta",
            "total_emission"
        ]

class ReportSimpleSerializer(ModelSerializer):
    
    id = serializers.IntegerField(read_only=False, allow_null=True, default=None)
    
    class Meta:
        model = Report
        fields = [
            "id",
            "names", 
            "date",
            "year",
            "deltas"
        ]

class ReportSerializer(ModelSerializer):

    def create(self, validated_data):
        report_entries_data = validated_data.pop('report_entries', [])
        report = Report.objects.create(**validated_data)
        
        for re_data in report_entries_data :
            ReportEntry.objects.create(**re_data, report=report)
            
        report.save()

        return report
    
    def update(self, instance, validated_data):
        report_entries_data = validated_data.pop('report_entries', [])
        instance.names = validated_data.get("names")
        instance.year = validated_data.get("year")
        instance.date = validated_data.get("date")

        # create modifications if not
        ids_list = []
        for re_data in report_entries_data:
            if not re_data.get("id") :
                report_entry = ReportEntry.objects.create(report=instance, **re_data)
                ids_list += [report_entry.id]
            else :
                report_entry = ReportEntry.objects.get(id=re_data.get("id"))
                # copy report entry if already linked to another report 
                if report_entry.report.id!=instance.id :
                    report_entry.id = None
                    report_entry.report = instance
                    report_entry.save()
                ids_list += [report_entry.id]
        
        # delete unlinked modified source
        ReportEntry.objects.filter(report=instance).exclude(id__in=ids_list).delete()
        instance.save()

        return instance

    
    id = serializers.IntegerField(read_only=False, allow_null=True, default=None)
    report_entries = ReportEntrySerializer(many=True, read_only=False, required=False, allow_null=False)
    
    class Meta:
        model = Report
        fields = [
            "id",
            "names", 
            "date",
            "year",
            "report_entries",
            "deltas"
        ]


        