from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'advisor'

urlpatterns = [
    # Ana sayfa
    path('', views.home, name='home'),
    
    # Kullanıcı kayıt ve giriş
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='advisor/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Finansal bilgi formu
    path('profile/', views.profile_form, name='profile_form'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Yatırım tavsiyesi
    path('recommendation/', views.investment_recommendation, name='investment_recommendation'),
    path('result/<int:result_id>/', views.investment_result, name='investment_result'),
    
    # PDF indirme
    path('result/<int:result_id>/pdf/', views.download_pdf, name='download_pdf'),

    # Piyasa ve portföy sayfaları
    path('piyasa/', views.piyasa_verileri, name='piyasa'),
    path('portfoyum/', views.my_portfolio, name='my_portfolio'),

    # Portföy performans verisi API endpoint
    path('portfolio-performance/', views.portfolio_performance_view, name='portfolio_performance'),
    path('portfolio-performance-data/', views.portfolio_performance_data, name='portfolio_performance_data'),
    path('haberler/', views.news, name='news'),

]
