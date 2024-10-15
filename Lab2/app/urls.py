from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('participants/<int:participant_id>/', participant),
    path('tenders/<int:tender_id>/', tender),
]