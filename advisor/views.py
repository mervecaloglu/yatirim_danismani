from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from pycoingecko import CoinGeckoAPI
import feedparser  # HABERLER İÇİN

from .forms import CustomUserCreationForm, UserProfileForm, PortfolioForm
from .models import UserProfile, InvestmentRecommendation, UserInvestmentResult, PortfolioEntry

cg = CoinGeckoAPI()

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

# Kullanıcı Portföyü Görüntüle ve Ekle + İstatistik Kartları + Varlık Detay Kartları
@login_required
def my_portfolio(request):
    entries = PortfolioEntry.objects.filter(user=request.user)
    symbol_to_id = {
        'BTCUSDT': 'bitcoin',
        'ETHUSDT': 'ethereum',
        # Diğer sembolleri ekleyin
    }

    portfolio_details = []
    total_invested = 0
    total_current_value = 0

    for entry in entries:
        total_invested += float(entry.amount_usd)
        coingecko_id = symbol_to_id.get(entry.symbol.upper())
        current_price = None
        change_24h = None
        if coingecko_id:
            try:
                prices = cg.get_coin_market_chart_by_id(id=coingecko_id, vs_currency='usd', days=2)['prices']
                if len(prices) >= 2:
                    first_price = prices[0][1]
                    last_price = prices[-1][1]
                    current_price = last_price
                    change_24h = ((last_price - first_price) / first_price) * 100
                else:
                    current_price = prices[-1][1]
                    change_24h = 0
            except Exception:
                current_price = None
                change_24h = None
        current_value = float(entry.amount_usd) * (current_price if current_price else 1)
        total_current_value += current_value

        portfolio_details.append({
            'asset_name': entry.asset_name,
            'amount_usd': entry.amount_usd,
            'added_at': entry.added_at,
            'current_price': current_price,
            'change_24h': change_24h,
            'current_value': current_value,
        })

    daily_profit_percent = 0
    if total_invested > 0:
        daily_profit_percent = ((total_current_value - total_invested) / total_invested) * 100

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
        'entries': portfolio_details,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'daily_profit_percent': daily_profit_percent,
        'title': 'Portföyüm'
    }
    return render(request, 'advisor/portfolio.html', context)

# Kar/Zarar Grafiği Verisi (API)
@login_required
def portfolio_performance_data(request):
    user = request.user
    portfolio = PortfolioEntry.objects.filter(user=user)
    symbol_to_id = {
        'BTCUSDT': 'bitcoin',
        'ETHUSDT': 'ethereum',
        # Gerekirse ekleyin
    }
    daily_totals = {}
    for entry in portfolio:
        coingecko_id = symbol_to_id.get(entry.symbol.upper())
        if not coingecko_id:
            continue
        prices = cg.get_coin_market_chart_by_id(id=coingecko_id, vs_currency='usd', days=7)['prices']
        for timestamp, price in prices:
            date_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
            value = float(entry.amount_usd) * price
            if date_str in daily_totals:
                daily_totals[date_str] += value
            else:
                daily_totals[date_str] = value
    sorted_dates = sorted(daily_totals.keys())
    sorted_values = [daily_totals[date] for date in sorted_dates]
    daily_changes = []
    for i in range(len(sorted_values)):
        if i == 0:
            daily_changes.append(0)
        else:
            change = sorted_values[i] - sorted_values[i-1]
            daily_changes.append(round(change, 2))
    data = {
        'dates': sorted_dates,
        'total_values': sorted_values,
        'daily_changes': daily_changes,
    }
    return JsonResponse(data)

@login_required
def portfolio_performance_view(request):
    return render(request, 'advisor/portfolio_performance.html', {'title': 'Portföy Performans Grafiği'})

# Haberler View (RSS ile Apikey’siz)
def news(request):
    rss_urls = [
        'https://tr.investing.com/rss/news_285.rss',  # Investing.com - Ekonomi Haberleri Türkçe
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=BTC-USD,ETH-USD,TSLA,AAPL&region=US&lang=en-US',
    ]
    all_news = []
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            all_news.append({
                'title': entry.title,
                'link': entry.link,
                'summary': entry.summary if hasattr(entry, 'summary') else '',
                'published': entry.published if hasattr(entry, 'published') else '',
                'source': feed.feed.title if hasattr(feed.feed, 'title') else 'Kaynak',
            })
    all_news.sort(key=lambda x: x['published'], reverse=True)
    return render(request, 'advisor/news.html', {'all_news': all_news, 'title': 'Yatırım Haberleri'})
