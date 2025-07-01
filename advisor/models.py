from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(verbose_name="Yaş", validators=[MinValueValidator(18), MaxValueValidator(100)])
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Aylık Gelir (TL)")
    current_savings = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Mevcut Birikim (TL)")

    INVESTMENT_DURATION_CHOICES = [
        ('short', 'Kısa Vadeli (1-2 yıl)'),
        ('medium', 'Orta Vadeli (3-5 yıl)'),
        ('long', 'Uzun Vadeli (5+ yıl)'),
    ]
    investment_duration = models.CharField(
        max_length=10,
        choices=INVESTMENT_DURATION_CHOICES,
        verbose_name="Yatırım Süresi"
    )

    # Geliştirilmiş risk soruları
    risk_goal = models.PositiveIntegerField(
        verbose_name="Yatırım yapma amacınız en çok hangisine uygundur?",
        help_text="0: Günlük harcama için, 1: Güvence için, 2: Varlık artırmak için, 3: Uzun vadeli servet için",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    risk_time_horizon = models.PositiveIntegerField(
        verbose_name="Yatırımı ne kadar süre dokunmadan tutarsınız?",
        help_text="0: <1 yıl, 1: 1-2 yıl, 2: 3-5 yıl, 3: 5+ yıl",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    risk_drawdown = models.PositiveIntegerField(
        verbose_name="Yatırımınız %15 düşerse nasıl davranırsınız?",
        help_text="0: Satarım, 1: Beklerim, 2: Alırım, 3: Umursamam",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    risk_opportunity = models.PositiveIntegerField(
        verbose_name="Yeni yükselen yatırım fırsatlarına yaklaşımınız?",
        help_text="0: İlgilenmem, 1: Araştırırım, 2: Az yatırırım, 3: Hemen girerim",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    risk_market_crash = models.PositiveIntegerField(
        verbose_name="Ekonomik kriz durumunda tavrınız nedir?",
        help_text="0: Çıkarım, 1: Kısmen satarım, 2: Beklerim, 3: Alım yaparım",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    risk_emergency_cash = models.PositiveIntegerField(
        verbose_name="Acil durumlar için ne kadar nakit ayırırsınız?",
        help_text="0: Hiç, 1: 1-2 ay, 2: 3-5 ay, 3: 6+ ay",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    risk_income_dependence = models.PositiveIntegerField(
        verbose_name="Yatırım gelirine olan bağımlılığınız?",
        help_text="0: Tamamen, 1: Büyük ölçüde, 2: Kısmen, 3: Bağımsızım",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    risk_knowledge = models.PositiveIntegerField(
        verbose_name="Yatırım bilgisi düzeyiniz nedir?",
        help_text="0: Hiç yok, 1: Temel, 2: Orta, 3: İleri",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    risk_diversification = models.PositiveIntegerField(
        verbose_name="Portföy çeşitliliği hakkındaki görüşünüz?",
        help_text="0: Tek varlık yeter, 1: 2-3 varlık, 2: 4-5 varlık, 3: Mümkünse çok",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    risk_high_risk_pref = models.PositiveIntegerField(
        verbose_name="Yüksek riskli yatırımlara yaklaşımınız?",
        help_text="0: Uzak dururum, 1: Denerim, 2: Kısmen değerlendiririm, 3: Severim",
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )

    RISK_PROFILE_CHOICES = [
        ('low', 'Düşük Risk'),
        ('medium', 'Orta Risk'),
        ('high', 'Yüksek Risk'),
    ]
    risk_profile = models.CharField(
        max_length=10,
        choices=RISK_PROFILE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Risk Profili"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"

    def __str__(self):
        return f"{self.user.username} - {self.get_risk_profile_display()}"

    def calculate_risk_profile(self):
        score = (
            self.risk_goal + self.risk_time_horizon + self.risk_drawdown +
            self.risk_opportunity + self.risk_market_crash + self.risk_emergency_cash +
            self.risk_income_dependence + self.risk_knowledge +
            self.risk_diversification + self.risk_high_risk_pref
        )
        if score <= 12:
            return 'low'
        elif score <= 24:
            return 'medium'
        else:
            return 'high'

    def save(self, *args, **kwargs):
        self.risk_profile = self.calculate_risk_profile()
        super().save(*args, **kwargs)



class InvestmentRecommendation(models.Model):
    risk_profile = models.CharField(
        max_length=10,
        choices=UserProfile.RISK_PROFILE_CHOICES,
        verbose_name="Risk Profili"
    )
    investment_duration = models.CharField(
        max_length=10,
        choices=UserProfile.INVESTMENT_DURATION_CHOICES,
        verbose_name="Yatırım Süresi"
    )
    deposit_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Mevduat Yüzdesi"
    )
    gold_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Altın Yüzdesi"
    )
    stock_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Hisse Senedi Yüzdesi"
    )
    crypto_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Kripto Para Yüzdesi"
    )
    expected_annual_return = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        verbose_name="Tahmini Yıllık Getiri (%)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Yatırım Önerisi"
        verbose_name_plural = "Yatırım Önerileri"
        unique_together = ['risk_profile', 'investment_duration']

    def __str__(self):
        return f"{self.get_risk_profile_display()} - {self.get_investment_duration_display()}"

    def clean(self):
        from django.core.exceptions import ValidationError
        total = self.deposit_percentage + self.gold_percentage + self.stock_percentage + self.crypto_percentage
        if total != 100:
            raise ValidationError("Yatırım türlerinin yüzdeleri toplamı 100 olmalıdır.")

    def get_investment_breakdown(self):
        return {
            'Mevduat': self.deposit_percentage,
            'Altın': self.gold_percentage,
            'Hisse Senedi': self.stock_percentage,
            'Kripto Para': self.crypto_percentage,
        }


class UserInvestmentResult(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="Kullanıcı Profili")
    recommendation = models.ForeignKey(InvestmentRecommendation, on_delete=models.CASCADE, verbose_name="Yatırım Önerisi")
    investment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Yatırım Tutarı (TL)"
    )
    projected_return_1_year = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="1 Yıllık Tahmini Getiri (TL)"
    )
    projected_return_5_year = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="5 Yıllık Tahmini Getiri (TL)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Kullanıcı Yatırım Sonucu"
        verbose_name_plural = "Kullanıcı Yatırım Sonuçları"

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.created_at.strftime('%d.%m.%Y')}"


class PortfolioEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset_name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=30)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.asset_name} - {self.amount_usd} USD"
