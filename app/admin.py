from django.contrib import admin

from .models import *

admin.site.register(Participant)
admin.site.register(Tender)
admin.site.register(ParticipantTender)
