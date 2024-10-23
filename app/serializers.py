from rest_framework import serializers

from .models import *


class ParticipantSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, participant):
        if participant.image:
            return participant.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Participant
        fields = "__all__"


class ParticipantItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_image(self, participant):
        if participant.image:
            return participant.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    def get_value(self, participant):
        return self.context.get("value")

    class Meta:
        model = Participant
        fields = ("id", "name", "image", "value")


class TenderSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, tender):
        return tender.owner.username

    def get_moderator(self, tender):
        if tender.moderator:
            return tender.moderator.username
            
    def get_participants(self, tender):
        items = ParticipantTender.objects.filter(tender=tender)
        return [ParticipantItemSerializer(item.participant, context={"value": item.value}).data for item in items]

    class Meta:
        model = Tender
        fields = '__all__'


class TendersSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, tender):
        return tender.owner.username

    def get_moderator(self, tender):
        if tender.moderator:
            return tender.moderator.username

    class Meta:
        model = Tender
        fields = "__all__"


class ParticipantTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantTender
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
