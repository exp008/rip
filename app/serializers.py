import os

from rest_framework import serializers

from .models import *


class ParticipantsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, participant):
        if participant.image:
            return participant.image.url.replace("minio", os.getenv("IP_ADDRESS"), 1)

        return f"http://{os.getenv("IP_ADDRESS")}:9000/images/default.png"

    class Meta:
        model = Participant
        fields = ("id", "name", "status", "phone", "image", 'clas')


class ParticipantSerializer(ParticipantsSerializer):
    class Meta:
        model = Participant
        fields = "__all__"


class ParticipantAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ("name", "description", "phone")


class TendersSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)
    won = serializers.SerializerMethodField()

    def get_won(self, tender):
        items = tender.participanttender_set.all()
        # Возвращает название победителя тендера
        return next((item.participant.name for item in items if item.won), None)

    class Meta:
        model = Tender
        fields = "__all__"


class TenderSerializer(TendersSerializer):
    participants = serializers.SerializerMethodField()

    def get_participants(self, tender):
        items = tender.participanttender_set.all()
        return [ParticipantItemSerializer(item.participant, context={"won": item.won}).data for item in items]


class ParticipantItemSerializer(ParticipantSerializer):
    won = serializers.SerializerMethodField()

    def get_won(self, _):
        return self.context.get("won")

    class Meta:
        model = Participant
        fields = ("id", "name", "status", "phone", "image", "won")


class ParticipantTenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantTender
        fields = "__all__"

    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', "is_superuser")


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


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
