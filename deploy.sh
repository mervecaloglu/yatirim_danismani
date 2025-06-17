#!/bin/bash

# Kişiselleştirilmiş Yatırım Tavsiyesi Sistemi - Deployment Script
# Ubuntu VPS için otomatik kurulum scripti

echo "=== Kişiselleştirilmiş Yatırım Tavsiyesi Sistemi Kurulumu ==="

# Sistem güncellemeleri
echo "Sistem güncelleniyor..."
sudo apt update && sudo apt upgrade -y

# Gerekli paketleri yükle
echo "Gerekli paketler yükleniyor..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# PostgreSQL kurulumu
echo "PostgreSQL yapılandırılıyor..."
sudo -u postgres psql -c "CREATE DATABASE investment_advisor;"
sudo -u postgres psql -c "CREATE USER advisor_user WITH PASSWORD 'strong_password_here';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE investment_advisor TO advisor_user;"

# Proje dizini oluştur
PROJECT_DIR="/var/www/investment_advisor"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Sanal ortam oluştur
echo "Python sanal ortamı oluşturuluyor..."
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate

# Gerekli paketleri yükle
echo "Python paketleri yükleniyor..."
pip install --upgrade pip
pip install django==5.2 pillow reportlab matplotlib gunicorn psycopg2-binary

# Django projesi kurulumu
echo "Django projesi yapılandırılıyor..."
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py load_recommendations

# Gunicorn servis dosyası oluştur
echo "Gunicorn servisi yapılandırılıyor..."
sudo tee /etc/systemd/system/investment-advisor.service > /dev/null <<EOF
[Unit]
Description=Investment Advisor Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/investment_advisor.sock investment_advisor.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Nginx konfigürasyonu
echo "Nginx yapılandırılıyor..."
sudo tee /etc/nginx/sites-available/investment-advisor > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root $PROJECT_DIR;
    }
    
    location /media/ {
        root $PROJECT_DIR;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/investment_advisor.sock;
    }
}
EOF

# Nginx sitesini aktifleştir
sudo ln -sf /etc/nginx/sites-available/investment-advisor /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Servisleri başlat
echo "Servisler başlatılıyor..."
sudo systemctl daemon-reload
sudo systemctl start investment-advisor
sudo systemctl enable investment-advisor
sudo systemctl restart nginx

# Güvenlik ayarları
echo "Güvenlik ayarları yapılandırılıyor..."
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

# Dosya izinleri
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

echo "=== Kurulum Tamamlandı! ==="
echo "Web siteniz şu adreste çalışıyor: http://$(curl -s ifconfig.me)"
echo ""
echo "Admin paneli için superuser oluşturmayı unutmayın:"
echo "cd $PROJECT_DIR && source venv/bin/activate && python manage.py createsuperuser"
echo ""
echo "Logları kontrol etmek için:"
echo "sudo journalctl -u investment-advisor"
echo "sudo tail -f /var/log/nginx/error.log"

