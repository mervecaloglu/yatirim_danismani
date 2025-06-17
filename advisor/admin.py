from django.contrib import admin
from .models import UserProfile, InvestmentRecommendation, UserInvestmentResult


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'monthly_income', 'current_savings', 'investment_duration', 'risk_profile', 'created_at']
    list_filter = ['risk_profile', 'investment_duration', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['risk_profile', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'age')
        }),
        ('Finansal Bilgiler', {
            'fields': ('monthly_income', 'current_savings', 'investment_duration')
        }),
        ('Risk Profili Soruları', {
            'fields': ('risk_question_1', 'risk_question_2', 'risk_question_3', 'risk_question_4')
        }),
        ('Hesaplanan Değerler', {
            'fields': ('risk_profile',),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InvestmentRecommendation)
class InvestmentRecommendationAdmin(admin.ModelAdmin):
    list_display = ['risk_profile', 'investment_duration', 'deposit_percentage', 'gold_percentage', 
                   'stock_percentage', 'crypto_percentage', 'expected_annual_return']
    list_filter = ['risk_profile', 'investment_duration']
    
    fieldsets = (
        ('Profil Bilgileri', {
            'fields': ('risk_profile', 'investment_duration')
        }),
        ('Yatırım Dağılımı (%)', {
            'fields': ('deposit_percentage', 'gold_percentage', 'stock_percentage', 'crypto_percentage'),
            'description': 'Yüzdelerin toplamı 100 olmalıdır.'
        }),
        ('Getiri Beklentisi', {
            'fields': ('expected_annual_return',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Kaydetmeden önce yüzdelerin toplamını kontrol et
        """
        total = obj.deposit_percentage + obj.gold_percentage + obj.stock_percentage + obj.crypto_percentage
        if total != 100:
            from django.contrib import messages
            messages.error(request, f"Yatırım türlerinin yüzdeleri toplamı {total}. 100 olmalıdır.")
            return
        super().save_model(request, obj, form, change)


@admin.register(UserInvestmentResult)
class UserInvestmentResultAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'recommendation', 'investment_amount', 
                   'projected_return_1_year', 'projected_return_5_year', 'created_at']
    list_filter = ['recommendation__risk_profile', 'recommendation__investment_duration', 'created_at']
    search_fields = ['user_profile__user__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user_profile__user', 'recommendation')


# Admin site başlık ve başlık ayarları
admin.site.site_header = "Yatırım Tavsiyesi Sistemi"
admin.site.site_title = "Yatırım Tavsiyesi Admin"
admin.site.index_title = "Yönetim Paneli"

