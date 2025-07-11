# Generated by Django 4.2.23 on 2025-07-01 17:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advisor', '0004_alter_userprofile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='risk_diversification',
            field=models.PositiveIntegerField(help_text='0: Tek varlık yeter, 1: 2-3 varlık, 2: 4-5 varlık, 3: Mümkünse çok', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Portföy çeşitliliği hakkındaki görüşünüz?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_drawdown',
            field=models.PositiveIntegerField(help_text='0: Satarım, 1: Beklerim, 2: Alırım, 3: Umursamam', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Yatırımınız %15 düşerse nasıl davranırsınız?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_emergency_cash',
            field=models.PositiveIntegerField(help_text='0: Hiç, 1: 1-2 ay, 2: 3-5 ay, 3: 6+ ay', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Acil durumlar için ne kadar nakit ayırırsınız?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_goal',
            field=models.PositiveIntegerField(help_text='0: Günlük harcama için, 1: Güvence için, 2: Varlık artırmak için, 3: Uzun vadeli servet için', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Yatırım yapma amacınız en çok hangisine uygundur?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_high_risk_pref',
            field=models.PositiveIntegerField(help_text='0: Uzak dururum, 1: Denerim, 2: Kısmen değerlendiririm, 3: Severim', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Yüksek riskli yatırımlara yaklaşımınız?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_income_dependence',
            field=models.PositiveIntegerField(help_text='0: Tamamen, 1: Büyük ölçüde, 2: Kısmen, 3: Bağımsızım', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Yatırım gelirine olan bağımlılığınız?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_knowledge',
            field=models.PositiveIntegerField(help_text='0: Hiç yok, 1: Temel, 2: Orta, 3: İleri', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Yatırım bilgisi düzeyiniz nedir?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_market_crash',
            field=models.PositiveIntegerField(help_text='0: Çıkarım, 1: Kısmen satarım, 2: Beklerim, 3: Alım yaparım', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Ekonomik kriz durumunda tavrınız nedir?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_opportunity',
            field=models.PositiveIntegerField(help_text='0: İlgilenmem, 1: Araştırırım, 2: Az yatırırım, 3: Hemen girerim', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Yeni yükselen yatırım fırsatlarına yaklaşımınız?'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='risk_time_horizon',
            field=models.PositiveIntegerField(help_text='0: <1 yıl, 1: 1-2 yıl, 2: 3-5 yıl, 3: 5+ yıl', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)], verbose_name='Yatırımı ne kadar süre dokunmadan tutarsınız?'),
        ),
    ]
