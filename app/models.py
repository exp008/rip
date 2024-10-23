from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Participant(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название", blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(default="default.png", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)

    phone = models.CharField(blank=True)

    def get_image(self):
        return self.image.url.replace("minio", "localhost", 1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
        db_table = "participants"


class Tender(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", null=True, related_name='moderator')

    description = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "Тендер №" + str(self.pk)

    def get_participants(self):
        return [
            setattr(item.participant, "value", item.value) or item.participant
            for item in ParticipantTender.objects.filter(tender=self)
        ]

    class Meta:
        verbose_name = "Тендер"
        verbose_name_plural = "Тендеры"
        ordering = ('-date_formation',)
        db_table = "tenders"


class ParticipantTender(models.Model):
    participant = models.ForeignKey(Participant, models.DO_NOTHING, blank=True, null=True)
    tender = models.ForeignKey(Tender, models.DO_NOTHING, blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "participant_tender"
        unique_together = ('participant', 'tender')
