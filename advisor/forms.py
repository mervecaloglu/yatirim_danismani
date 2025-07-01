# advisor/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, PortfolioEntry

# Kullanıcı Kayıt Formu (CustomUserCreationForm)
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-posta")
    first_name = forms.CharField(max_length=30, required=True, label="Ad")
    last_name = forms.CharField(max_length=30, required=True, label="Soyad")
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['username'].label = 'Kullanıcı Adı'
        self.fields['password1'].label = 'Şifre'
        self.fields['password2'].label = 'Şifre Tekrarı'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

# Kullanıcı Profili ve Risk Soruları Formu
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'age', 'monthly_income', 'current_savings', 'investment_duration',
            'risk_goal', 'risk_time_horizon', 'risk_drawdown', 'risk_opportunity',
            'risk_market_crash', 'risk_emergency_cash', 'risk_income_dependence',
            'risk_knowledge', 'risk_diversification', 'risk_high_risk_pref'
        ]
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_savings': forms.NumberInput(attrs={'class': 'form-control'}),
            'investment_duration': forms.Select(attrs={'class': 'form-control'}),
            'risk_goal': forms.RadioSelect(),
            'risk_time_horizon': forms.RadioSelect(),
            'risk_drawdown': forms.RadioSelect(),
            'risk_opportunity': forms.RadioSelect(),
            'risk_market_crash': forms.RadioSelect(),
            'risk_emergency_cash': forms.RadioSelect(),
            'risk_income_dependence': forms.RadioSelect(),
            'risk_knowledge': forms.RadioSelect(),
            'risk_diversification': forms.RadioSelect(),
            'risk_high_risk_pref': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['risk_goal'].widget.choices = [
            (0, "Kısa vadeli harcama"),
            (1, "Beklenmedik durumlar"),
            (2, "Varlık artırma"),
            (3, "Uzun vadeli büyüme"),
        ]
        self.fields['risk_time_horizon'].widget.choices = [
            (0, "1 yıldan az"),
            (1, "1-2 yıl"),
            (2, "3-5 yıl"),
            (3, "5+ yıl"),
        ]
        self.fields['risk_drawdown'].widget.choices = [
            (0, "Hemen satarım"),
            (1, "Beklerim"),
            (2, "Eklerim"),
            (3, "Umursamam"),
        ]
        self.fields['risk_opportunity'].widget.choices = [
            (0, "Hiç ilgilenmem"),
            (1, "Temkinli"),
            (2, "Denerim"),
            (3, "Hızlıca yatırım yaparım"),
        ]
        self.fields['risk_market_crash'].widget.choices = [
            (0, "Çıkarım"),
            (1, "Bir kısmını satarım"),
            (2, "Aynen devam"),
            (3, "Alım yaparım"),
        ]
        self.fields['risk_emergency_cash'].widget.choices = [
            (0, "Hiç"),
            (1, "1-2 ay"),
            (2, "3-5 ay"),
            (3, "6+ ay"),
        ]
        self.fields['risk_income_dependence'].widget.choices = [
            (0, "Tamamen"),
            (1, "Büyük oranda"),
            (2, "Az"),
            (3, "Bağımsız"),
        ]
        self.fields['risk_knowledge'].widget.choices = [
            (0, "Yok"),
            (1, "Az"),
            (2, "Orta"),
            (3, "İleri"),
        ]
        self.fields['risk_diversification'].widget.choices = [
            (0, "Sadece bir varlık"),
            (1, "2-3 varlık"),
            (2, "4-5 varlık"),
            (3, "Çok çeşit"),
        ]
        self.fields['risk_high_risk_pref'].widget.choices = [
            (0, "Hiç"),
            (1, "Nadiren"),
            (2, "Zaman zaman"),
            (3, "Sık sık"),
        ]
        # Bootstrap için radio'lara class ekle
        for field_name in [
            'risk_goal', 'risk_time_horizon', 'risk_drawdown', 'risk_opportunity',
            'risk_market_crash', 'risk_emergency_cash', 'risk_income_dependence',
            'risk_knowledge', 'risk_diversification', 'risk_high_risk_pref'
        ]:
            self.fields[field_name].widget.attrs.update({'class': 'form-check-input'})

# Portföy Ekleme Formu
class PortfolioForm(forms.ModelForm):
    class Meta:
        model = PortfolioEntry
        fields = ['asset_name', 'symbol', 'amount_usd']
        widgets = {
            'asset_name': forms.TextInput(attrs={'class': 'form-control'}),
            'symbol': forms.TextInput(attrs={'class': 'form-control'}),
            'amount_usd': forms.NumberInput(attrs={'class': 'form-control'}),
        }
