# Generated by Django 4.2 on 2025-07-01 13:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("advisor", "0002_portfolioentry"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="risk_question_1",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="risk_question_2",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="risk_question_3",
        ),
        migrations.RemoveField(
            model_name="userprofile",
            name="risk_question_4",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_diversification",
            field=models.PositiveIntegerField(
                default=1,
                help_text="0: Sadece bir varlık, 1: 2-3 varlık, 2: 4-5 varlık, 3: Çok çeşit",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Varlık çeşitliliği hakkındaki görüşünüz?",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_drawdown",
            field=models.PositiveIntegerField(
                default=0,
                help_text="0: Hemen satarım, 1: Beklerim, 2: Eklerim, 3: Umursamam",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Yatırımınız %10 değer kaybederse tutumunuz?",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_emergency_cash",
            field=models.PositiveIntegerField(
                default=0,
                help_text="0: Hiç, 1: 1-2 ay, 2: 3-5 ay, 3: 6+ ay",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Acil durumda ne kadar nakdiniz var?",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_goal",
            field=models.PositiveIntegerField(
                default=0,
                help_text="0: Kısa vadeli harcama, 1: Beklenmedik durumlar, 2: Varlık artırma, 3: Uzun vadeli büyüme",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Yatırımınızın temel amacı nedir?",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_high_risk_pref",
            field=models.PositiveIntegerField(
                default=0,
                help_text="0: Hiç, 1: Nadiren, 2: Zaman zaman, 3: Sık sık",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Yüksek riskli yatırımlara ilginiz?",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_income_dependence",
            field=models.PositiveIntegerField(
                default=0,
                help_text="0: Tamamen, 1: Büyük oranda, 2: Az, 3: Bağımsız",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Yatırımdan elde ettiğiniz gelire bağımlılık düzeyiniz?",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_knowledge",
            field=models.PositiveIntegerField(
                default=0,
                help_text="0: Yok, 1: Az, 2: Orta, 3: İleri",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Yatırım bilgisi düzeyiniz?",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_market_crash",
            field=models.PositiveIntegerField(
                default=0,
                help_text="0: Çıkarım, 1: Bir kısmını satarım, 2: Aynen devam, 3: Alım yaparım",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Piyasa krizi yaşanırsa ne yaparsınız?",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_opportunity",
            field=models.PositiveIntegerField(
                default=0,
                help_text="0: Hiç ilgilenmem, 1: Temkinli, 2: Denerim, 3: Hızlıca yatırım yaparım",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Yeni yatırım fırsatlarına yaklaşımınız?",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="userprofile",
            name="risk_time_horizon",
            field=models.PositiveIntegerField(
                default=0,
                help_text="0: 1 yıldan az, 1: 1-2 yıl, 2: 3-5 yıl, 3: 5+ yıl",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="Yatırım süreniz ne kadar?",
            ),
            preserve_default=False,
        ),
    ]
