from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """
    Özelleştirilmiş kullanıcı kayıt formu
    """
    email = forms.EmailField(required=True, label="E-posta")
    first_name = forms.CharField(max_length=30, required=True, label="Ad")
    last_name = forms.CharField(max_length=30, required=True, label="Soyad")
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Form alanlarına Bootstrap sınıfları ekle
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Türkçe etiketler
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


class UserProfileForm(forms.ModelForm):
    """
    Kullanıcı finansal bilgileri ve risk profili formu
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'age', 'monthly_income', 'current_savings', 'investment_duration',
            'risk_question_1', 'risk_question_2', 'risk_question_3', 'risk_question_4'
        ]
        
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '18', 'max': '100'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'current_savings': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'investment_duration': forms.Select(attrs={'class': 'form-control'}),
            'risk_question_1': forms.RadioSelect(),
            'risk_question_2': forms.RadioSelect(),
            'risk_question_3': forms.RadioSelect(),
            'risk_question_4': forms.RadioSelect(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Risk soruları için seçenekler
        risk_choices = [
            (0, '0 - En düşük'),
            (1, '1 - Düşük'),
            (2, '2 - Yüksek'),
            (3, '3 - En yüksek'),
        ]
        
        # Her risk sorusu için özel seçenekler
        self.fields['risk_question_1'].widget.choices = [
            (0, '0 - Kesinlikle evet'),
            (1, '1 - Evet'),
            (2, '2 - Hayır'),
            (3, '3 - Kesinlikle hayır'),
        ]
        
        self.fields['risk_question_2'].widget.choices = [
            (0, '0 - Hiç yok'),
            (1, '1 - Az'),
            (2, '2 - Orta'),
            (3, '3 - Çok yüksek'),
        ]
        
        self.fields['risk_question_3'].widget.choices = [
            (0, '0 - Çok rahatsız eder'),
            (1, '1 - Rahatsız eder'),
            (2, '2 - Az rahatsız eder'),
            (3, '3 - Hiç rahatsız etmez'),
        ]
        
        self.fields['risk_question_4'].widget.choices = [
            (0, '0 - Kesinlikle hayır'),
            (1, '1 - Hayır'),
            (2, '2 - Evet'),
            (3, '3 - Kesinlikle evet'),
        ]
        
        # Widget sınıflarını güncelle
        for field_name in ['risk_question_1', 'risk_question_2', 'risk_question_3', 'risk_question_4']:
            self.fields[field_name].widget.attrs.update({'class': 'form-check-input'})
    
    def save(self, commit=True):
        """
        Formu kaydederken risk profilini otomatik hesapla
        """
        profile = super().save(commit=False)
        if commit:
            profile.save()
        return profile

