import requests
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_tender():
    return Tender.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_participants(request):
    participant_name = request.GET.get("participant_name", "")

    participants = Participant.objects.filter(status=1)

    if participant_name:
        participants = participants.filter(name__icontains=participant_name)

    serializer = ParticipantSerializer(participants, many=True)

    draft_tender = get_draft_tender()

    resp = {
        "participants": serializer.data,
        "participants_count": len(serializer.data),
        "draft_tender": draft_tender.pk if draft_tender else None
    }

    return Response(resp)


@api_view(["GET"])
def get_participant_by_id(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)
    serializer = ParticipantSerializer(participant, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_participant(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)

    image = request.data.get("image")
    if image is not None:
        participant.image = image
        participant.save()

    serializer = ParticipantSerializer(participant, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_participant(request):
    Participant.objects.create()

    participants = Participant.objects.filter(status=1)
    serializer = ParticipantSerializer(participants, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_participant(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)
    participant.status = 2
    participant.save()

    participants = Participant.objects.filter(status=1)
    serializer = ParticipantSerializer(participants, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_participant_to_tender(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)

    draft_tender = get_draft_tender()

    if draft_tender is None:
        draft_tender = Tender.objects.create()
        draft_tender.owner = get_user()
        draft_tender.date_created = timezone.now()
        draft_tender.save()

    if ParticipantTender.objects.filter(tender=draft_tender, participant=participant).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
    item = ParticipantTender.objects.create()
    item.tender = draft_tender
    item.participant = participant
    item.save()

    serializer = TenderSerializer(draft_tender)
    return Response(serializer.data["participants"])


@api_view(["POST"])
def update_participant_image(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)

    image = request.data.get("image")
    if image is not None:
        participant.image = image
        participant.save()

    serializer = ParticipantSerializer(participant)

    return Response(serializer.data)


@api_view(["GET"])
def search_tenders(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    tenders = Tender.objects.exclude(status__in=[1, 5])

    if status > 0:
        tenders = tenders.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        tenders = tenders.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        tenders = tenders.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = TendersSerializer(tenders, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_tender_by_id(request, tender_id):
    if not Tender.objects.filter(pk=tender_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tender = Tender.objects.get(pk=tender_id)
    serializer = TenderSerializer(tender, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_tender(request, tender_id):
    if not Tender.objects.filter(pk=tender_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tender = Tender.objects.get(pk=tender_id)
    serializer = TenderSerializer(tender, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, tender_id):
    if not Tender.objects.filter(pk=tender_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tender = Tender.objects.get(pk=tender_id)

    if tender.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tender.status = 2
    tender.date_formation = timezone.now()
    tender.save()

    serializer = TenderSerializer(tender, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, tender_id):
    if not Tender.objects.filter(pk=tender_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tender = Tender.objects.get(pk=tender_id)

    if tender.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tender.date_complete = timezone.now()
    tender.status = request_status
    tender.moderator = get_moderator()
    tender.save()

    serializer = TenderSerializer(tender, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_tender(request, tender_id):
    if not Tender.objects.filter(pk=tender_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tender = Tender.objects.get(pk=tender_id)

    if tender.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tender.status = 5
    tender.save()

    serializer = TenderSerializer(tender, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_participant_from_tender(request, tender_id, participant_id):
    if not ParticipantTender.objects.filter(tender_id=tender_id, participant_id=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ParticipantTender.objects.get(tender_id=tender_id, participant_id=participant_id)
    item.delete()

    tender = Tender.objects.get(pk=tender_id)

    serializer = TenderSerializer(tender, many=False)
    participants = serializer.data["participants"]

    if len(participants) == 0:
        tender.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(participants)


@api_view(["PUT"])
def update_participant_in_tender(request, tender_id, participant_id):
    if not ParticipantTender.objects.filter(participant_id=participant_id, tender_id=tender_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ParticipantTender.objects.get(participant_id=participant_id, tender_id=tender_id)

    serializer = ParticipantTenderSerializer(item, data=request.data,  partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)