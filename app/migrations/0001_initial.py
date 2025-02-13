# Generated by Django 4.2.7 on 2025-02-12 19:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(max_length=500, verbose_name='Описание')),
                ('status', models.IntegerField(choices=[(1, 'Действует'), (2, 'Удалена')], default=1, verbose_name='Статус')),
                ('image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Фото')),
                ('phone', models.CharField(verbose_name='Телефон')),
                ('clas', models.CharField(verbose_name='Класс')),
            ],
            options={
                'verbose_name': 'Участник',
                'verbose_name_plural': 'Участники',
                'db_table': 'participants',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Tender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Введён'), (2, 'В работе'), (3, 'Завершен'), (4, 'Отклонен'), (5, 'Удален')], default=1, verbose_name='Статус')),
                ('date_created', models.DateTimeField(blank=True, null=True, verbose_name='Дата создания')),
                ('date_formation', models.DateTimeField(blank=True, null=True, verbose_name='Дата формирования')),
                ('date_complete', models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')),
                ('description', models.CharField(blank=True, null=True)),
                ('moderator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='moderator', to=settings.AUTH_USER_MODEL, verbose_name='Сотрудник')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='owner', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
            ],
            options={
                'verbose_name': 'Тендер',
                'verbose_name_plural': 'Тендеры',
                'db_table': 'tenders',
                'ordering': ('-date_formation',),
            },
        ),
        migrations.CreateModel(
            name='ParticipantTender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('won', models.BooleanField(default=False, verbose_name='Выиграл')),
                ('participant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.participant')),
                ('tender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.tender')),
            ],
            options={
                'verbose_name': 'м-м',
                'verbose_name_plural': 'м-м',
                'db_table': 'participant_tender',
                'ordering': ('pk',),
            },
        ),
        migrations.AddConstraint(
            model_name='participanttender',
            constraint=models.UniqueConstraint(fields=('participant', 'tender'), name='participant_tender_constraint'),
        ),
    ]
