from django.core.management.base import BaseCommand
from advisor.models import InvestmentRecommendation


class Command(BaseCommand):
    help = 'Varsayılan yatırım önerilerini veritabanına yükler'

    def handle(self, *args, **options):
        """
        Kullanıcının istediği 6-9 farklı kombinasyon için yatırım önerileri
        """
        recommendations = [
            # Düşük Risk Kombinasyonları
            {
                'risk_profile': 'low',
                'investment_duration': 'short',
                'deposit_percentage': 80,
                'gold_percentage': 20,
                'stock_percentage': 0,
                'crypto_percentage': 0,
                'expected_annual_return': 8.0,
            },
            {
                'risk_profile': 'low',
                'investment_duration': 'medium',
                'deposit_percentage': 70,
                'gold_percentage': 25,
                'stock_percentage': 5,
                'crypto_percentage': 0,
                'expected_annual_return': 9.0,
            },
            {
                'risk_profile': 'low',
                'investment_duration': 'long',
                'deposit_percentage': 60,
                'gold_percentage': 30,
                'stock_percentage': 10,
                'crypto_percentage': 0,
                'expected_annual_return': 10.0,
            },
            
            # Orta Risk Kombinasyonları
            {
                'risk_profile': 'medium',
                'investment_duration': 'short',
                'deposit_percentage': 50,
                'gold_percentage': 30,
                'stock_percentage': 20,
                'crypto_percentage': 0,
                'expected_annual_return': 11.0,
            },
            {
                'risk_profile': 'medium',
                'investment_duration': 'medium',
                'deposit_percentage': 40,
                'gold_percentage': 30,
                'stock_percentage': 30,
                'crypto_percentage': 0,
                'expected_annual_return': 12.0,
            },
            {
                'risk_profile': 'medium',
                'investment_duration': 'long',
                'deposit_percentage': 30,
                'gold_percentage': 25,
                'stock_percentage': 40,
                'crypto_percentage': 5,
                'expected_annual_return': 13.0,
            },
            
            # Yüksek Risk Kombinasyonları
            {
                'risk_profile': 'high',
                'investment_duration': 'short',
                'deposit_percentage': 30,
                'gold_percentage': 20,
                'stock_percentage': 40,
                'crypto_percentage': 10,
                'expected_annual_return': 15.0,
            },
            {
                'risk_profile': 'high',
                'investment_duration': 'medium',
                'deposit_percentage': 20,
                'gold_percentage': 15,
                'stock_percentage': 50,
                'crypto_percentage': 15,
                'expected_annual_return': 17.0,
            },
            {
                'risk_profile': 'high',
                'investment_duration': 'long',
                'deposit_percentage': 10,
                'gold_percentage': 10,
                'stock_percentage': 60,
                'crypto_percentage': 20,
                'expected_annual_return': 20.0,
            },
        ]

        created_count = 0
        updated_count = 0

        for rec_data in recommendations:
            recommendation, created = InvestmentRecommendation.objects.get_or_create(
                risk_profile=rec_data['risk_profile'],
                investment_duration=rec_data['investment_duration'],
                defaults=rec_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Yeni öneri oluşturuldu: {recommendation.get_risk_profile_display()} - '
                        f'{recommendation.get_investment_duration_display()}'
                    )
                )
            else:
                # Mevcut öneriyi güncelle
                for key, value in rec_data.items():
                    setattr(recommendation, key, value)
                recommendation.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Mevcut öneri güncellendi: {recommendation.get_risk_profile_display()} - '
                        f'{recommendation.get_investment_duration_display()}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nToplam: {created_count} yeni öneri oluşturuldu, {updated_count} öneri güncellendi.'
            )
        )

