import rest_registration.api.serializers as registration_serializers
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import JSONField, ModelSerializer
from tapio.models import Company, Report, Source, Unit, UserProfile


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
    
    names = JSONField(read_only=False, allow_null=False, required=False)

    class Meta:
        model = Unit
        fields = '__all__'


class SourceSerializer(ModelSerializer):
    
    # names = serializers.JSONField(default=dict, allow_null=True)
    # # company = serializers.JSONField(read_only=False, allow_null=True, required=False, default=None)
    # company = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=False, many=False)
    # description = serializers.CharField(max_length=250, allow_null=True)    
    # unit = serializers.PrimaryKeyRelatedField(
    #     many=False,
    #     allow_null=False,
    #     required=True,
    #     read_only=False,
    #     queryset=Unit.objects.all(),
    # )
    # value = serializers.FloatField(allow_null=False)    
    # emission_factor = serializers.FloatField(allow_null=False)    
    # total_emission = serializers.FloatField(allow_null=True)    
    # lifetime = serializers.FloatField(allow_null=True)    
    # acquisition_year = serializers.FloatField(allow_null=True)

    class Meta:
        model = Source
        fields = '__all__'


class ReportSerializer(ModelSerializer):
    
    class Meta:
        model = Report
        fields = '__all__'



        