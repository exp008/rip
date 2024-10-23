from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Participant, Tender, ParticipantTender


def index(request):
    participant_name = request.GET.get("participant_name", "")
    participants = Participant.objects.filter(status=1)

    if participant_name:
        participants = participants.filter(name__icontains=participant_name)

    draft_tender = get_draft_tender()

    context = {
        "participant_name": participant_name,
        "participants": participants
    }

    if draft_tender:
        context["participants_count"] = len(draft_tender.get_participants())
        context["draft_tender"] = draft_tender

    return render(request, "participants_page.html", context)


def add_participant_to_draft_tender(request, participant_id):
    participant = Participant.objects.get(pk=participant_id)

    draft_tender = get_draft_tender()

    if draft_tender is None:
        draft_tender = Tender.objects.create()
        draft_tender.owner = get_current_user()
        draft_tender.date_created = timezone.now()
        draft_tender.save()

    if ParticipantTender.objects.filter(tender=draft_tender, participant=participant).exists():
        return redirect("/")

    item = ParticipantTender(
        tender=draft_tender,
        participant=participant
    )
    item.save()

    return redirect("/")


def participant_details(request, participant_id):
    context = {
        "participant": Participant.objects.get(id=participant_id)
    }

    return render(request, "participant_page.html", context)


def delete_tender(request, tender_id):
    if not Tender.objects.filter(pk=tender_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE tenders SET status=5 WHERE id = %s", [tender_id])

    return redirect("/")


def tender(request, tender_id):
    if not Tender.objects.filter(pk=tender_id).exists():
        return redirect("/")

    tender = Tender.objects.get(id=tender_id)
    if tender.status == 5:
        return redirect("/")

    context = {
        "tender": tender,
    }

    return render(request, "tender_page.html", context)


def get_draft_tender():
    return Tender.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()