import random
from datetime import timedelta
import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .services.predictImage import predictImageData
from .utils import identity_user, get_session


def get_draft_tender(request):
    user = identity_user(request)

    if user is None:
        return None

    tender = Tender.objects.filter(owner=user).filter(status=1).first()

    return tender


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'participant_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_participants(request):
    participant_name = request.GET.get("participant_name", "")

    participants = Participant.objects.filter(status=1)

    if participant_name:
        participants = participants.filter(name__icontains=participant_name)

    serializer = ParticipantsSerializer(participants, many=True)

    draft_tender = get_draft_tender(request)

    resp = {
        "participants": serializer.data,
        "participants_count": ParticipantTender.objects.filter(tender=draft_tender).count() if draft_tender else None,
        "draft_tender_id": draft_tender.pk if draft_tender else None
    }

    return Response(resp)


@api_view(["GET"])
def get_participant_by_id(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)
    serializer = ParticipantSerializer(participant)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=ParticipantSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_participant(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)

    serializer = ParticipantSerializer(participant, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=ParticipantAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def create_participant(request):
    serializer = ParticipantAddSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    participant = Participant.objects.create(**serializer.validated_data)

    image = request.data.get("image")
    if image:
        participant.image = image
        participant.save()
        participant.clas = predictImageData(image)
        participant.save()

    participants = Participant.objects.filter(status=1)
    serializer = ParticipantsSerializer(participants, many=True)

    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_participant_image(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    participant.image = image
    participant.save()

    participant.clas = predictImageData(image)
    participant.save()

    serializer = ParticipantSerializer(participant)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_participant(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)
    participant.status = 2
    participant.save()

    participant = Participant.objects.filter(status=1)
    serializer = ParticipantSerializer(participant, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_participant_to_tender(request, participant_id):
    if not Participant.objects.filter(pk=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    participant = Participant.objects.get(pk=participant_id)

    draft_tender = get_draft_tender(request)

    if draft_tender is None:
        draft_tender = Tender.objects.create()
        draft_tender.date_created = timezone.now()
        draft_tender.owner = identity_user(request)
        draft_tender.save()

    if ParticipantTender.objects.filter(tender=draft_tender, participant=participant).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = ParticipantTender.objects.create()
    item.tender = draft_tender
    item.participant = participant
    item.save()

    serializer = TenderSerializer(draft_tender)
    return Response(serializer.data["participants"])


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_tenders(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    tenders = Tender.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        tenders = tenders.filter(owner=user)

    if status_id > 0:
        tenders = tenders.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        tenders = tenders.filter(date_formation__gte=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        tenders = tenders.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = TendersSerializer(tenders, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_tender_by_id(request, tender_id):
    user = identity_user(request)

    if not Tender.objects.filter(pk=tender_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tender = Tender.objects.get(pk=tender_id)

    if not user.is_superuser and tender.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TenderSerializer(tender)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=TenderSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_tender(request, tender_id):
    user = identity_user(request)

    if not Tender.objects.filter(pk=tender_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tender = Tender.objects.get(pk=tender_id)
    serializer = TenderSerializer(tender, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, tender_id):
    user = identity_user(request)

    if not Tender.objects.filter(pk=tender_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tender = Tender.objects.get(pk=tender_id)

    if tender.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tender.status = 2
    tender.date_formation = timezone.now()
    tender.save()

    serializer = TenderSerializer(tender)

    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    )
)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, tender_id):
    if not Tender.objects.filter(pk=tender_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tender = Tender.objects.get(pk=tender_id)

    if tender.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        participant = random.choice(tender.participanttender_set.all())
        participant.won = True
        participant.save()

    tender.status = request_status
    tender.date_complete = timezone.now()
    tender.moderator = identity_user(request)
    tender.save()

    serializer = TenderSerializer(tender)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_tender(request, tender_id):
    user = identity_user(request)

    if not Tender.objects.filter(pk=tender_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    tender = Tender.objects.get(pk=tender_id)

    if tender.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    tender.status = 5
    tender.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_participant_from_tender(request, tender_id, participant_id):
    user = identity_user(request)

    if not Tender.objects.filter(pk=tender_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ParticipantTender.objects.filter(tender_id=tender_id, participant_id=participant_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ParticipantTender.objects.get(tender_id=tender_id, participant_id=participant_id)
    item.delete()

    tender = Tender.objects.get(pk=tender_id)

    serializer = TenderSerializer(tender)
    participants = serializer.data["participants"]

    return Response(participants)


@swagger_auto_schema(method='PUT', request_body=ParticipantTenderSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_participant_in_tender(request, tender_id, participant_id):
    user = identity_user(request)

    if not Tender.objects.filter(pk=tender_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not ParticipantTender.objects.filter(participant_id=participant_id, tender_id=tender_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = ParticipantTender.objects.get(participant_id=participant_id, tender_id=tender_id)

    serializer = ParticipantTenderSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
