from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/participants/', search_participants),  # GET
    path('api/participants/<int:participant_id>/', get_participant_by_id),  # GET
    path('api/participants/<int:participant_id>/update/', update_participant),  # PUT
    path('api/participants/<int:participant_id>/update_image/', update_participant_image),  # POST
    path('api/participants/<int:participant_id>/delete/', delete_participant),  # DELETE
    path('api/participants/create/', create_participant),  # POST
    path('api/participants/<int:participant_id>/add_to_tender/', add_participant_to_tender),  # POST

    # Набор методов для заявок
    path('api/tenders/', search_tenders),  # GET
    path('api/tenders/<int:tender_id>/', get_tender_by_id),  # GET
    path('api/tenders/<int:tender_id>/update/', update_tender),  # PUT
    path('api/tenders/<int:tender_id>/update_status_user/', update_status_user),  # PUT
    path('api/tenders/<int:tender_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/tenders/<int:tender_id>/delete/', delete_tender),  # DELETE

    # Набор методов для м-м
    path('api/tenders/<int:tender_id>/update_participant/<int:participant_id>/', update_participant_in_tender),  # PUT
    path('api/tenders/<int:tender_id>/delete_participant/<int:participant_id>/', delete_participant_from_tender),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]
