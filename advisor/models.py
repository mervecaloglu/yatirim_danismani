from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """
    Kullanıcının finansal bilgilerini ve risk profilini tutan model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
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
    
    # Risk profili soruları (0-3 arası puanlama)
    risk_question_1 = models.PositiveIntegerField(
        verbose_name="Paranızı kısa sürede harcamayı planlıyor musunuz?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Kesinlikle evet, 1: Evet, 2: Hayır, 3: Kesinlikle hayır"
    )
    risk_question_2 = models.PositiveIntegerField(
        verbose_name="Piyasa dalgalanmalarına ne kadar toleransınız var?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Hiç yok, 1: Az, 2: Orta, 3: Çok yüksek"
    )
    risk_question_3 = models.PositiveIntegerField(
        verbose_name="Yatırımınızın aniden %10 değer kaybetmesi sizi ne kadar rahatsız eder?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Çok rahatsız eder, 1: Rahatsız eder, 2: Az rahatsız eder, 3: Hiç rahatsız etmez"
    )
    risk_question_4 = models.PositiveIntegerField(
        verbose_name="Yüksek kazanç için beklemeyi kabul eder misiniz?",
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="0: Kesinlikle hayır, 1: Hayır, 2: Evet, 3: Kesinlikle evet"
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
        """
        Risk profili sorularının puanlarına göre risk profilini hesaplar
        0-4: Düşük Risk, 5-7: Orta Risk, 8+: Yüksek Risk
        """
        total_score = (
            self.risk_question_1 + 
            self.risk_question_2 + 
            self.risk_question_3 + 
            self.risk_question_4
        )
        
        if total_score <= 4:
            return 'low'
        elif total_score <= 7:
            return 'medium'
        else:
            return 'high'
    
    def save(self, *args, **kwargs):
        """
        Kaydetmeden önce risk profilini otomatik hesapla
        """
        self.risk_profile = self.calculate_risk_profile()
        super().save(*args, **kwargs)


class InvestmentRecommendation(models.Model):
    """
    Risk profili ve yatırım süresine göre yatırım önerilerini tutan model
    Admin panelinden düzenlenebilir
    """
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
    
    # Yatırım türleri ve yüzdeleri
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
    
    # Tahmini yıllık getiri oranı
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
        """
        Yüzdelerin toplamının 100 olduğunu kontrol et
        """
        from django.core.exceptions import ValidationError
        total = self.deposit_percentage + self.gold_percentage + self.stock_percentage + self.crypto_percentage
        if total != 100:
            raise ValidationError("Yatırım türlerinin yüzdeleri toplamı 100 olmalıdır.")
    
    def get_investment_breakdown(self):
        """
        Yatırım dağılımını dictionary olarak döndürür
        """
        return {
            'Mevduat': self.deposit_percentage,
            'Altın': self.gold_percentage,
            'Hisse Senedi': self.stock_percentage,
            'Kripto Para': self.crypto_percentage,
        }


class UserInvestmentResult(models.Model):
    """
    Kullanıcının aldığı yatırım tavsiyesini ve sonuçlarını tutan model
    """
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="Kullanıcı Profili")
    recommendation = models.ForeignKey(InvestmentRecommendation, on_delete=models.CASCADE, verbose_name="Yatırım Önerisi")
    
    # Hesaplanan değerler
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

