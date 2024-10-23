import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


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

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_tenders():
    users = User.objects.filter(is_superuser=False)
    moderators = User.objects.filter(is_superuser=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    participants = Participant.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        add_tender(status, participants, users, moderators)

    add_tender(1, participants, users, moderators)

    print("Заявки добавлены")


def add_tender(status, participants, users, moderators):
    tender = Tender.objects.create()
    tender.status = status

    if tender.status in [3, 4]:
        tender.date_complete = random_date()
        tender.date_formation = tender.date_complete - random_timedelta()
        tender.date_created = tender.date_formation - random_timedelta()
    else:
        tender.date_formation = random_date()
        tender.date_created = tender.date_formation - random_timedelta()

    tender.owner = random.choice(users)
    tender.moderator = random.choice(moderators)

    tender.description = "Описание тендера"
    tender.date = random_date()

    for participant in random.sample(list(participants), 3):
        item = ParticipantTender(
            tender=tender,
            participant=participant,
            value=random.randint(1, 100) * 100000
        )
        item.save()

    tender.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_participants()
        add_tenders()



















