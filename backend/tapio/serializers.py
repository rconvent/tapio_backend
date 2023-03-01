import rest_registration.api.serializers as registration_serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from tapio.models import *


def pprint(*args, **kwargs):
    # print("\n\n")
    return print("\n\nDEBUG", *args, end="\n\n", **kwargs)
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

    def to_representation(self, value):
        data = super().to_representation(value)
        return data

    def to_internal_value(self, data):
        return super().to_internal_value(data)

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



class SourceSimpleSerializer(ModelSerializer):

    class Meta:
        model = Source
        fields = [
            "id",
            "names",
            "value",
            "emission_factor",
            "total_emission",
            "lifetime",
            "acquisition_year",
        ]

class SourceSerializer(SourceSimpleSerializer):
    
    
    def create(self, validated_data):
        modified_sources_data = validated_data.pop('modifiedSources')
        source = Source.objects.create(**validated_data)
        
        # create modified source if not existing else only link to source
        for ms in modified_sources_data:
            if "id" not in ms :
                ModifiedSource.objects.create(source=source, **ms)
            else :
                ms = ModifiedSource.objects.get(ms.get("id"))
                if ms.source :
                    raise ValidationError({"Modified Source" : f"Modified Source {ms.id} has already a linked source"})
                ms.source = source
                ms.save()

        return source
    
    def update(self, instance, validated_data):
        modified_sources_data = validated_data.pop('modifiedSources')
        serializer = SourceSimpleSerializer(instance, data=validated_data)
        serializer.is_valid(raise_exception=True)
        source = serializer.save()

        # create modified source if not existing else only link to source
        for ms in modified_sources_data:
            pprint()
            if "id" not in ms :
                raise ValidationError({"Modified Source" : f"Modified Source Id should be provided in the patch data"})
            else :
                ms = ModifiedSource.objects.get(ms.get("id"))
                if ms.source.id!=source.id :
                    raise ValidationError({"Modified Source" : f"Modified Source {ms.id} has another a linked source"})
                ms.save()
        
        return source

    modifiedSources = ModifiedSourceSerializer(many=True, read_only=False, required=False, allow_null=False)

    class Meta:
        model = Source
        fields = [
            "id",
            "names",
            "value",
            "emission_factor",
            "total_emission",
            "lifetime",
            "acquisition_year",
            "modifiedSources"
        ]



class ReportSerializer(ModelSerializer):
    
    class Meta:
        model = Report
        fields = '__all__'



        