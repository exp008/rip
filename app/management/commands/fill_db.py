from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

from .utils import *
from app.models import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_participants():
    Participant.objects.create(
        name="Госстрой",
        description="Федеральное агентство по строительству и жилищно-коммунальному хозяйству (Госстрой) является федеральным органом исполнительной власти, осуществляющим функции по оказанию государственных услуг, управлению государственным имуществом в сфере строительства, градостроительства, промышленности строительных материалов.",
        phone="+7 (495) 123-45-67",
        image="1.png"
    )

    Participant.objects.create(
        name="МинФин",
        description="Министерство финансов Российской Федерации — федеральное министерство Российской Федерации, обеспечивающее проведение единой финансовой политики, а также осуществляющее общее руководство в области организации финансов в Российской Федерации.",
        phone="+7 (495) 234-56-78",
        image="2.png"
    )

    Participant.objects.create(
        name="ФСБ",
        description="Федеральная служба безопасности Российской Федерации — федеральный орган исполнительной власти, в пределах своих полномочий осуществляющий государственное управление в области обеспечения безопасности Российской Федерации, борьбы с терроризмом, защиты и охраны государственной границы Российской Федерации.",
        phone="+7 (495) 354-81-35",
        image="3.png"
    )

    Participant.objects.create(
        name="Минздрав",
        description="Министерство здравоохранения Российской Федерации — федеральный орган исполнительной власти Российской Федерации, осуществляющий функции по выработке государственной политики и нормативно-правовому регулированию в сфере здравоохранения, обязательного медицинского страхования, обращения лекарственных средств.",
        phone="+7 (495) 456-78-90",
        image="4.png"
    )

    Participant.objects.create(
        name="АП Кремль",
        description="Руководитель Администрации президента Российской Федерации (АП РФ) — федеральный государственный гражданский служащий, выполняющий непосредственное руководство работой Администрации президента России, общее руководство которой выполняет президент Российской Федерации.",
        phone="+7 (495) 567-89-01",
        image="5.png"
    )

    Participant.objects.create(
        name="МВД",
        description="Министерство внутренних дел Российской Федерации (МВД России) является федеральным органом исполнительной власти, осуществляющим функции по выработке и реализации государственной политики и нормативно-правовому регулированию в сфере внутренних дел, а также по выработке государственной политики в сфере миграции.",
        phone="+7 (495) 678-90-12",
        image="6.png"
    )

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_tenders():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    participants = Participant.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_tender(status, participants, owner, moderators)

    add_tender(1, participants, users[0], moderators)
    add_tender(2, participants, users[0], moderators)
    add_tender(3, participants, users[0], moderators)
    add_tender(4, participants, users[0], moderators)
    add_tender(5, participants, users[0], moderators)

    for _ in range(10):
        status = random.randint(2, 5)
        add_tender(status, participants, users[0], moderators)


def add_tender(status, participants, owner, moderators):
    tender = Tender.objects.create()
    tender.status = status

    if status in [3, 4]:
        tender.moderator = random.choice(moderators)
        tender.date_complete = random_date()
        tender.date_formation = tender.date_complete - random_timedelta()
        tender.date_created = tender.date_formation - random_timedelta()
    else:
        tender.date_formation = random_date()
        tender.date_created = tender.date_formation - random_timedelta()

    tender.description = "Описание тендера"

    tender.owner = owner

    items = []
    for participant in random.sample(list(participants), 3):
        item = ParticipantTender(
            tender=tender,
            participant=participant,
            won=False
        )
        item.save()
        items.append(item)

    if status == 3:
        participant = random.choice(items)
        participant.won = True
        participant.save()

    tender.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_participants()
        add_tenders()
