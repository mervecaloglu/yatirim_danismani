from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')  # GUI olmayan backend kullan
import matplotlib.pyplot as plt
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

from .forms import CustomUserCreationForm, UserProfileForm
from .models import UserProfile, InvestmentRecommendation, UserInvestmentResult


def home(request):
    """
    Ana sayfa view'ı
    """
    context = {
        'title': 'Kişiselleştirilmiş Yatırım Tavsiyesi Sistemi'
    }
    return render(request, 'advisor/home.html', context)


def register(request):
    """
    Kullanıcı kayıt view'ı
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Kayıt işlemi başarılı! Şimdi finansal bilgilerinizi girebilirsiniz.')
            return redirect('advisor:profile_form')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Kayıt Ol'
    }
    return render(request, 'advisor/register.html', context)


@login_required
def profile_form(request):
    """
    Kullanıcı profil formu view'ı
    """
    try:
        profile = UserProfile.objects.get(user=request.user)
        # Eğer profil varsa düzenleme sayfasına yönlendir
        return redirect('advisor:profile_edit')
    except UserProfile.DoesNotExist:
        # Profil yoksa yeni oluştur
        if request.method == 'POST':
            form = UserProfileForm(request.POST)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, 'Finansal bilgileriniz başarıyla kaydedildi!')
                return redirect('advisor:investment_recommendation')
        else:
            form = UserProfileForm()
    
    context = {
        'form': form,
        'title': 'Finansal Bilgiler'
    }
    return render(request, 'advisor/profile_form.html', context)


@login_required
def profile_edit(request):
    """
    Kullanıcı profil düzenleme view'ı
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Finansal bilgileriniz başarıyla güncellendi!')
            return redirect('advisor:investment_recommendation')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'title': 'Finansal Bilgileri Düzenle'
    }
    return render(request, 'advisor/profile_edit.html', context)


@login_required
def investment_recommendation(request):
    """
    Yatırım tavsiyesi hesaplama ve gösterme view'ı
    """
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Önce finansal bilgilerinizi girmeniz gerekiyor.')
        return redirect('advisor:profile_form')
    
    # Risk profili ve yatırım süresine göre öneri bul
    try:
        recommendation = InvestmentRecommendation.objects.get(
            risk_profile=profile.risk_profile,
            investment_duration=profile.investment_duration
        )
    except InvestmentRecommendation.DoesNotExist:
        messages.error(request, 'Bu profil için henüz bir yatırım önerisi tanımlanmamış.')
        return redirect('advisor:profile_edit')
    
    # Yatırım tutarını hesapla (mevcut birikimlerin %80'i)
    investment_amount = profile.current_savings * Decimal('0.8')
    
    # Gelecekteki getiri hesaplamaları
    annual_return_rate = recommendation.expected_annual_return / 100
    projected_return_1_year = investment_amount * (1 + annual_return_rate)
    projected_return_5_year = investment_amount * ((1 + annual_return_rate) ** 5)
    
    # Sonucu kaydet
    result, created = UserInvestmentResult.objects.get_or_create(
        user_profile=profile,
        recommendation=recommendation,
        defaults={
            'investment_amount': investment_amount,
            'projected_return_1_year': projected_return_1_year,
            'projected_return_5_year': projected_return_5_year,
        }
    )
    
    if not created:
        # Mevcut sonucu güncelle
        result.investment_amount = investment_amount
        result.projected_return_1_year = projected_return_1_year
        result.projected_return_5_year = projected_return_5_year
        result.save()
    
    return redirect('advisor:investment_result', result_id=result.id)


@login_required
def investment_result(request, result_id):
    """
    Yatırım sonucu gösterme view'ı
    """
    result = get_object_or_404(UserInvestmentResult, id=result_id, user_profile__user=request.user)
    
    # Grafik oluştur
    chart_data = create_investment_chart(result.recommendation)
    
    context = {
        'result': result,
        'chart_data': chart_data,
        'title': 'Yatırım Tavsiyeniz'
    }
    return render(request, 'advisor/investment_result.html', context)


def create_investment_chart(recommendation):
    """
    Yatırım dağılımı için pasta grafiği oluşturur
    """
    # Veri hazırlama
    labels = []
    sizes = []
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    breakdown = recommendation.get_investment_breakdown()
    for investment_type, percentage in breakdown.items():
        if percentage > 0:
            labels.append(f'{investment_type}\n%{percentage}')
            sizes.append(percentage)
    
    # Grafik oluştur
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors[:len(sizes)], autopct='%1.1f%%', startangle=90)
    plt.title('Önerilen Yatırım Dağılımı', fontsize=16, fontweight='bold')
    plt.axis('equal')
    
    # Grafiği base64 string'e çevir
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    return graphic


@login_required
def download_pdf(request, result_id):
    """
    Yatırım tavsiyesini PDF olarak indirme view'ı
    """
    result = get_object_or_404(UserInvestmentResult, id=result_id, user_profile__user=request.user)
    
    # HTTP response oluştur
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="yatirim_tavsiyesi_{result.user_profile.user.username}.pdf"'
    
    # PDF oluştur
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    # Başlık
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "Kişiselleştirilmiş Yatırım Tavsiyesi")
    
    # Kullanıcı bilgileri
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 100, "Kullanıcı Bilgileri:")
    
    p.setFont("Helvetica", 12)
    y_position = height - 120
    user_info = [
        f"Ad Soyad: {result.user_profile.user.first_name} {result.user_profile.user.last_name}",
        f"Yaş: {result.user_profile.age}",
        f"Aylık Gelir: {result.user_profile.monthly_income:,.2f} TL",
        f"Mevcut Birikim: {result.user_profile.current_savings:,.2f} TL",
        f"Yatırım Süresi: {result.user_profile.get_investment_duration_display()}",
        f"Risk Profili: {result.user_profile.get_risk_profile_display()}",
    ]
    
    for info in user_info:
        p.drawString(50, y_position, info)
        y_position -= 20
    
    # Yatırım önerisi
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position - 20, "Yatırım Önerisi:")
    
    p.setFont("Helvetica", 12)
    y_position -= 50
    breakdown = result.recommendation.get_investment_breakdown()
    for investment_type, percentage in breakdown.items():
        if percentage > 0:
            amount = result.investment_amount * Decimal(percentage) / 100
            p.drawString(50, y_position, f"{investment_type}: %{percentage} ({amount:,.2f} TL)")
            y_position -= 20
    
    # Getiri projeksiyonları
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y_position - 20, "Getiri Projeksiyonları:")
    
    p.setFont("Helvetica", 12)
    y_position -= 50
    projections = [
        f"Yatırım Tutarı: {result.investment_amount:,.2f} TL",
        f"1 Yıllık Tahmini Getiri: {result.projected_return_1_year:,.2f} TL",
        f"5 Yıllık Tahmini Getiri: {result.projected_return_5_year:,.2f} TL",
        f"Beklenen Yıllık Getiri Oranı: %{result.recommendation.expected_annual_return}",
    ]
    
    for projection in projections:
        p.drawString(50, y_position, projection)
        y_position -= 20
    
    # Uyarı metni
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 100, "Bu tavsiye sadece bilgilendirme amaçlıdır. Yatırım kararlarınızı verirken")
    p.drawString(50, 85, "profesyonel finansal danışmanlık almanız önerilir.")
    
    # Tarih
    from datetime import datetime
    p.drawString(50, 50, f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    
    p.showPage()
    p.save()
    
    return response

