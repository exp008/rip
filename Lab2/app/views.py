from django.shortcuts import render

participants = [
    {
        "id": 1,
        "name": "Госстрой",
        "description": "Федеральное агентство по строительству и жилищно-коммунальному хозяйству (Госстрой) является федеральным органом исполнительной власти, осуществляющим функции по оказанию государственных услуг, управлению государственным имуществом в сфере строительства, градостроительства, промышленности строительных материалов.",
        "phone": "+7 (495) 123-45-67",
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "МинФин",
        "description": "Министерство финансов Российской Федерации — федеральное министерство Российской Федерации, обеспечивающее проведение единой финансовой политики, а также осуществляющее общее руководство в области организации финансов в Российской Федерации.",
        "phone": "+7 (495) 234-56-78",
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "ФСБ",
        "description": "Федеральная служба безопасности Российской Федерации — федеральный орган исполнительной власти, в пределах своих полномочий осуществляющий государственное управление в области обеспечения безопасности Российской Федерации, борьбы с терроризмом, защиты и охраны государственной границы Российской Федерации.",
        "phone": "+7 (495) 354-81-35",
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Минздрав",
        "description": "Министерство здравоохранения Российской Федерации — федеральный орган исполнительной власти Российской Федерации, осуществляющий функции по выработке государственной политики и нормативно-правовому регулированию в сфере здравоохранения, обязательного медицинского страхования, обращения лекарственных средств.",
        "phone": "+7 (495) 456-78-90",
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "АП Кремль",
        "description": "Руководитель Администрации президента Российской Федерации (АП РФ) — федеральный государственный гражданский служащий, выполняющий непосредственное руководство работой Администрации президента России, общее руководство которой выполняет президент Российской Федерации.",
        "phone": "+7 (495) 567-89-01",
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "МВД",
        "description": "Министерство внутренних дел Российской Федерации (МВД России) является федеральным органом исполнительной власти, осуществляющим функции по выработке и реализации государственной политики и нормативно-правовому регулированию в сфере внутренних дел, а также по выработке государственной политики в сфере миграции.",
        "phone": "+7 (495) 678-90-12",
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_tender = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "description": "Описание тендера",
    "date": "12 октября 2024г",
    "participants": [
        {
            "id": 1,
            "value": 125000
        },
        {
            "id": 2,
            "value": 250000
        },
        {
            "id": 3,
            "value": 300000
        }
    ]
}


def getParticipantById(participant_id):
    for participant in participants:
        if participant["id"] == participant_id:
            return participant


def getParticipants():
    return participants


def searchParticipants(participant_name):
    res = []

    for participant in participants:
        if participant_name.lower() in participant["name"].lower():
            res.append(participant)

    return res


def getDraftTender():
    return draft_tender


def getTenderById(tender_id):
    return draft_tender


def index(request):
    participant_name = request.GET.get("participant_name", "")
    participants = searchParticipants(participant_name) if participant_name else getParticipants()
    draft_tender = getDraftTender()

    context = {
        "participants": participants,
        "participant_name": participant_name,
        "participants_count": len(draft_tender["participants"]),
        "draft_tender": draft_tender
    }

    return render(request, "participants_page.html", context)


def participant(request, participant_id):
    context = {
        "id": participant_id,
        "participant": getParticipantById(participant_id),
    }

    return render(request, "participant_page.html", context)


def tender(request, tender_id):
    tender = getTenderById(tender_id)
    participants = [
        {**getParticipantById(participant["id"]), "value": participant["value"]}
        for participant in tender["participants"]
    ]

    context = {
        "tender": tender,
        "participants": participants
    }

    return render(request, "tender_page.html", context)
