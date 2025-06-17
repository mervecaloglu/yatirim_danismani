# Kişiselleştirilmiş Yatırım Tavsiyesi Sistemi

Bu Django web uygulaması, kullanıcıların finansal durumlarına ve risk profillerine göre kişiselleştirilmiş yatırım önerileri sunan bir danışmanlık platformudur.

## Özellikler

### 1. Kullanıcı Yönetimi
- Django'nun yerleşik User modeliyle kullanıcı kayıt ve giriş sistemi
- Her kullanıcı sadece kendi verilerine erişebilir
- Güvenli oturum yönetimi

### 2. Finansal Bilgi Toplama
- Yaş, aylık gelir, mevcut birikim bilgileri
- Yatırım süresi seçimi (Kısa, Orta, Uzun vadeli)
- 4 soruluk risk profili belirleme anketi

### 3. Risk Profili Hesaplama
- Otomatik risk skoru hesaplama (0-12 puan arası)
- Düşük, Orta, Yüksek risk kategorileri
- Kullanıcının doğrudan seçim yapmasına gerek yok

### 4. Yatırım Tavsiye Motoru
- Risk profili ve yatırım süresine göre 9 farklı kombinasyon
- Mevduat, Altın, Hisse Senedi, Kripto para dağılımları
- Admin panelinden düzenlenebilir öneri oranları

### 5. Görsel Sonuç Sayfası
- Chart.js ile pasta grafik gösterimi
- Yatırım türleri ve yüzdelik dağılımlar
- 1 yıl ve 5 yıllık getiri projeksiyonları
- PDF indirme özelliği

### 6. Admin Paneli
- Django admin ile yatırım öneri oranları yönetimi
- Kullanıcı profilleri ve sonuçları görüntüleme
- Sistem ayarları düzenleme

## Kurulum

### Gereksinimler
- Python 3.8+
- Django 5.2
- Pillow (görsel işleme)
- ReportLab (PDF oluşturma)
- Matplotlib (grafik oluşturma)

### Adım Adım Kurulum

1. **Projeyi klonlayın veya indirin**
```bash
# Proje dosyalarını sunucuya yükleyin
```

2. **Sanal ortam oluşturun**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

3. **Gerekli paketleri yükleyin**
```bash
pip install -r requirements.txt
```

4. **Veritabanını oluşturun**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Varsayılan yatırım önerilerini yükleyin**
```bash
python manage.py load_recommendations
```

6. **Admin kullanıcısı oluşturun**
```bash
python manage.py createsuperuser
```

7. **Development server'ı başlatın**
```bash
python manage.py runserver 0.0.0.0:8000
```

## Production Deployment (Ubuntu VPS)

### 1. Sistem Güncellemeleri
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib -y
```

### 2. PostgreSQL Kurulumu (Opsiyonel)
```bash
sudo -u postgres createdb investment_advisor
sudo -u postgres createuser --interactive
```

### 3. Gunicorn ile Servis
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 investment_advisor.wsgi:application
```

### 4. Nginx Konfigürasyonu
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/your/project/static/;
    }

    location /media/ {
        alias /path/to/your/project/media/;
    }
}
```

### 5. Systemd Servis Dosyası
```ini
[Unit]
Description=Investment Advisor Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind unix:/path/to/your/project/investment_advisor.sock investment_advisor.wsgi:application

[Install]
WantedBy=multi-user.target
```

## Kullanım

### 1. Ana Sayfa
- Sistem hakkında bilgi
- Kayıt ol ve giriş yap linkleri

### 2. Kullanıcı Kaydı
- Temel kullanıcı bilgileri
- Otomatik giriş ve yönlendirme

### 3. Finansal Bilgi Formu
- Kişisel finansal bilgiler
- Risk profili belirleme soruları
- Otomatik risk skoru hesaplama

### 4. Yatırım Tavsiyesi
- Kişiselleştirilmiş portföy önerisi
- Görsel grafik gösterimi
- Getiri projeksiyonları
- PDF indirme seçeneği

### 5. Admin Paneli
- `/admin/` adresinden erişim
- Yatırım önerilerini düzenleme
- Kullanıcı verilerini görüntüleme

## Teknik Detaylar

### Proje Yapısı
```
investment_advisor/
├── investment_advisor/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── advisor/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   ├── urls.py
│   ├── templates/
│   ├── templatetags/
│   └── management/
├── static/
├── media/
├── requirements.txt
└── README.md
```

### Modeller
- **UserProfile**: Kullanıcı finansal bilgileri
- **InvestmentRecommendation**: Yatırım öneri şablonları
- **UserInvestmentResult**: Kullanıcı sonuçları

### Güvenlik
- CSRF koruması aktif
- Kullanıcı oturumu tabanlı erişim kontrolü
- Form validasyonları
- SQL injection koruması

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir. Ticari kullanım için gerekli lisansları kontrol ediniz.

## Destek

Herhangi bir sorun yaşarsanız:
1. Hata loglarını kontrol edin
2. Django debug modunu açın (sadece development için)
3. Veritabanı bağlantısını kontrol edin
4. Static dosyaların doğru servis edildiğini kontrol edin

## Önemli Notlar

⚠️ **Uyarı**: Bu sistem sadece bilgilendirme amaçlıdır. Gerçek yatırım kararları için profesyonel finansal danışmanlık alınmalıdır.

🔒 **Güvenlik**: Production ortamında DEBUG=False yapın ve SECRET_KEY'i güvenli tutun.

📊 **Performans**: Büyük kullanıcı sayıları için veritabanı optimizasyonu yapın.

