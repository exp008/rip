from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('participants/<int:participant_id>/', participant_details, name="participant_details"),
    path('participants/<int:participant_id>/add_to_tender/', add_participant_to_draft_tender, name="add_participant_to_draft_tender"),
    path('tenders/<int:tender_id>/delete/', delete_tender, name="delete_tender"),
    path('tenders/<int:tender_id>/', tender)
]
