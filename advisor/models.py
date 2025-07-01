from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(verbose_name="Yaş", validators=[MinValueValidator(18), MaxValueValidator(100)])
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Aylık Gelir (TL)")
    current_savings = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Mevcut Birikim (TL)")

    # Yatırım süresi seçenekleri
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

    # 10 risk sorusu (0-3 arası puanlama)
    risk_goal = models.PositiveIntegerField(
        verbose_name="Yatırımınızın temel amacı nedir?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Kısa vadeli harcama, 1: Beklenmedik durumlar, 2: Varlık artırma, 3: Uzun vadeli büyüme"
    )
    risk_time_horizon = models.PositiveIntegerField(
        verbose_name="Yatırım süreniz ne kadar?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: 1 yıldan az, 1: 1-2 yıl, 2: 3-5 yıl, 3: 5+ yıl"
    )
    risk_drawdown = models.PositiveIntegerField(
        verbose_name="Yatırımınız %10 değer kaybederse tutumunuz?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Hemen satarım, 1: Beklerim, 2: Eklerim, 3: Umursamam"
    )
    risk_opportunity = models.PositiveIntegerField(
        verbose_name="Yeni yatırım fırsatlarına yaklaşımınız?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Hiç ilgilenmem, 1: Temkinli, 2: Denerim, 3: Hızlıca yatırım yaparım"
    )
    risk_market_crash = models.PositiveIntegerField(
        verbose_name="Piyasa krizi yaşanırsa ne yaparsınız?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Çıkarım, 1: Bir kısmını satarım, 2: Aynen devam, 3: Alım yaparım"
    )
    risk_emergency_cash = models.PositiveIntegerField(
        verbose_name="Acil durumda ne kadar nakdiniz var?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Hiç, 1: 1-2 ay, 2: 3-5 ay, 3: 6+ ay"
    )
    risk_income_dependence = models.PositiveIntegerField(
        verbose_name="Yatırımdan elde ettiğiniz gelire bağımlılık düzeyiniz?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Tamamen, 1: Büyük oranda, 2: Az, 3: Bağımsız"
    )
    risk_knowledge = models.PositiveIntegerField(
        verbose_name="Yatırım bilgisi düzeyiniz?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Yok, 1: Az, 2: Orta, 3: İleri"
    )
    risk_diversification = models.PositiveIntegerField(
        verbose_name="Varlık çeşitliliği hakkındaki görüşünüz?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Sadece bir varlık, 1: 2-3 varlık, 2: 4-5 varlık, 3: Çok çeşit"
    )
    risk_high_risk_pref = models.PositiveIntegerField(
        verbose_name="Yüksek riskli yatırımlara ilginiz?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Hiç, 1: Nadiren, 2: Zaman zaman, 3: Sık sık"
    )

    # Hesaplanan risk profili
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
        total_score = (
            self.risk_goal +
            self.risk_time_horizon +
            self.risk_drawdown +
            self.risk_opportunity +
            self.risk_market_crash +
            self.risk_emergency_cash +
            self.risk_income_dependence +
            self.risk_knowledge +
            self.risk_diversification +
            self.risk_high_risk_pref
        )
        if total_score <= 10:
            return 'low'
        elif total_score <= 19:
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
