from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import requests
import certifi
from datetime import datetime

from .forms import CustomUserCreationForm, UserProfileForm, PortfolioForm
from .models import UserProfile, InvestmentRecommendation, UserInvestmentResult, PortfolioEntry

# Ana Sayfa
def home(request):
    context = {'title': 'Kişiselleştirilmiş Yatırım Tavsiyesi Sistemi'}
    return render(request, 'advisor/home.html', context)

# Kayıt Ol
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Kayıt işlemi başarılı! Şimdi finansal bilgilerinizi girebilirsiniz.')
            return redirect('advisor:profile_form')
    else:
        form = CustomUserCreationForm()

    return render(request, 'advisor/register.html', {'form': form, 'title': 'Kayıt Ol'})

# Profil Formu
@login_required
def profile_form(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        return redirect('advisor:profile_edit')
    except UserProfile.DoesNotExist:
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

    return render(request, 'advisor/profile_form.html', {'form': form, 'title': 'Finansal Bilgiler'})

# Profil Düzenle
@login_required
def profile_edit(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Finansal bilgileriniz başarıyla güncellendi!')
            return redirect('advisor:investment_recommendation')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'advisor/profile_edit.html', {'form': form, 'profile': profile, 'title': 'Finansal Bilgileri Düzenle'})

# Yatırım Tavsiyesi Hesaplama
@login_required
def investment_recommendation(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Önce finansal bilgilerinizi girmeniz gerekiyor.')
        return redirect('advisor:profile_form')

    try:
        recommendation = InvestmentRecommendation.objects.get(
            risk_profile=profile.risk_profile,
            investment_duration=profile.investment_duration
        )
    except InvestmentRecommendation.DoesNotExist:
        messages.error(request, 'Bu profil için henüz bir yatırım önerisi tanımlanmamış.')
        return redirect('advisor:profile_edit')

    investment_amount = profile.current_savings * Decimal('0.8')
    annual_return_rate = recommendation.expected_annual_return / 100
    projected_return_1_year = investment_amount * (1 + annual_return_rate)
    projected_return_5_year = investment_amount * ((1 + annual_return_rate) ** 5)

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
        result.investment_amount = investment_amount
        result.projected_return_1_year = projected_return_1_year
        result.projected_return_5_year = projected_return_5_year
        result.save()

    return redirect('advisor:investment_result', result_id=result.id)

# Yatırım Sonucu ve Grafik
@login_required
def investment_result(request, result_id):
    result = get_object_or_404(UserInvestmentResult, id=result_id, user_profile__user=request.user)
    chart_data = create_investment_chart(result.recommendation)

    return render(request, 'advisor/investment_result.html', {
        'result': result,
        'chart_data': chart_data,
        'title': 'Yatırım Tavsiyeniz'
    })

# Pasta Grafik Oluşturucu
def create_investment_chart(recommendation):
    labels = []
    sizes = []
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

    breakdown = recommendation.get_investment_breakdown()
    for investment_type, percentage in breakdown.items():
        if percentage > 0:
            labels.append(f'{investment_type}\n%{percentage}')
            sizes.append(percentage)

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors[:len(sizes)], autopct='%1.1f%%', startangle=90)
    plt.title('Önerilen Yatırım Dağılımı', fontsize=16, fontweight='bold')
    plt.axis('equal')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    return base64.b64encode(image_png).decode('utf-8')

# PDF Rapor İndir
@login_required
def download_pdf(request, result_id):
    result = get_object_or_404(UserInvestmentResult, id=result_id, user_profile__user=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="yatirim_tavsiyesi_{result.user_profile.user.username}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "Kişiselleştirilmiş Yatırım Tavsiyesi")

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 100, "Kullanıcı Bilgileri:")

    p.setFont("Helvetica", 12)
    y = height - 120
    user_info = [
        f"Ad Soyad: {result.user_profile.user.first_name} {result.user_profile.user.last_name}",
        f"Yaş: {result.user_profile.age}",
        f"Aylık Gelir: {result.user_profile.monthly_income:,.2f} TL",
        f"Mevcut Birikim: {result.user_profile.current_savings:,.2f} TL",
        f"Yatırım Süresi: {result.user_profile.get_investment_duration_display()}",
        f"Risk Profili: {result.user_profile.get_risk_profile_display()}",
    ]
    for info in user_info:
        p.drawString(50, y, info)
        y -= 20

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y - 20, "Yatırım Önerisi:")
    y -= 50
    p.setFont("Helvetica", 12)
    breakdown = result.recommendation.get_investment_breakdown()
    for investment_type, percentage in breakdown.items():
        if percentage > 0:
            amount = result.investment_amount * Decimal(percentage) / 100
            p.drawString(50, y, f"{investment_type}: %{percentage} ({amount:,.2f} TL)")
            y -= 20

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y - 20, "Getiri Projeksiyonları:")
    y -= 50
    projections = [
        f"Yatırım Tutarı: {result.investment_amount:,.2f} TL",
        f"1 Yıllık Tahmini Getiri: {result.projected_return_1_year:,.2f} TL",
        f"5 Yıllık Tahmini Getiri: {result.projected_return_5_year:,.2f} TL",
        f"Beklenen Yıllık Getiri Oranı: %{result.recommendation.expected_annual_return}",
    ]
    for projection in projections:
        p.drawString(50, y, projection)
        y -= 20

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 100, "Bu tavsiye sadece bilgilendirme amaçlıdır. Yatırım kararlarınızı verirken")
    p.drawString(50, 85, "profesyonel finansal danışmanlık almanız önerilir.")
    p.drawString(50, 50, f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    p.showPage()
    p.save()
    return response

# TradingView destekli Piyasa Fiyatları Paneli
def piyasa_verileri(request):
    semboller = {
        'Bitcoin (BTC/USDT)': 'BINANCE:BTCUSDT',
        'Ethereum (ETH/USDT)': 'BINANCE:ETHUSDT',
        'Altın (XAU/USD)': 'OANDA:XAUUSD',
        'THYAO (BIST)': 'BIST:THYAO'
    }
    return render(request, 'advisor/piyasa.html', {"semboller": semboller})

# Kullanıcı Portföyü Görüntüle ve Ekle
@login_required
def my_portfolio(request):
    entries = PortfolioEntry.objects.filter(user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, "Portföyünüze eklendi!")
            return redirect('advisor:my_portfolio')
    else:
        form = PortfolioForm()
    context = {
        'form': form,
        'entries': entries,
        'title': 'Portföyüm'
    }
    return render(request, 'advisor/portfolio.html', context)
