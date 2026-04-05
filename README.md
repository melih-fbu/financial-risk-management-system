# Çok Katmanlı Veri Tabanı Tabanlı Finansal Risk Yönetimi Sistemi

Sistem; altın ve gümüş fiyat verilerini saklar, portföy simülasyonu yapar, Historical VaR hesaplar, müşteri ve işlem yönetimi sunar, hassas müşteri verilerini şifreli saklar ve audit trail ile işlem geçmişini kaydeder.

Teknoloji yığını:

- Backend: Python, FastAPI, SQLAlchemy
- Veritabanı: PostgreSQL
- Frontend: React, Vite, Tailwind CSS, Recharts
- Güvenlik: `cryptography` Fernet

## Proje Özellikleri

- Historical VaR hesaplama
- Portföy simülasyonu
- Altın ve gümüş karşılaştırması
- Müşteri yönetimi
- İşlem yönetimi
- Veri şifreleme
- Audit trail
- React dashboard
- Çizgi grafik ve bar chart raporları

## Sistem Bileşenleri

### Backend

FastAPI tabanlı API katmanı aşağıdaki işlevleri sağlar:

- Metal fiyatlarının eklenmesi ve listelenmesi
- Portföy simülasyonu yapılması
- VaR hesaplanması
- Müşteri kaydı ve görüntüleme
- İşlem kaydı ve müşteri bazlı işlem takibi
- Özet raporlar ve risk raporları
- Şifreleme ve audit log işlemleri

### Frontend

React tabanlı arayüz aşağıdaki ekranları içerir:

- Ana sayfa
- Simülasyon sayfası
- Fiyat geçmişi sayfası
- Altın ve gümüş karşılaştırma sayfası

## Özellik Detayları

### 1. VaR Hesaplama

Sistem, tarihsel fiyat verilerinden günlük getirileri hesaplayarak %95 güven seviyesinde Historical VaR üretir.

### 2. Portföy Simülasyonu

Kullanıcı belirli bir tarihte yaptığı yatırımın güncel durumunu görebilir:

- başlangıç tutarı
- güncel değer
- kar / zarar
- VaR değeri

### 3. Altın / Gümüş Karşılaştırması

Aynı tutarın farklı tarih aralıklarında altın ve gümüşte nasıl performans gösterdiği karşılaştırılır:

- final tutar
- kar / zarar
- VaR %95

### 4. Müşteri Yönetimi

Sistem müşteri kayıtlarını tutar. Müşteriye ait işlemler ayrı olarak saklanır.

### 5. Veri Şifreleme

Müşteriye ait hassas alanlar veritabanında şifreli saklanır:

- `email`
- `phone`

Şifreleme için Fernet kullanılır. Anahtar `.env` dosyasındaki `ENCRYPTION_KEY` alanından okunur.

### 6. Audit Trail

Sistem müşteri ve işlem işlemlerinde audit log üretir. Bu sayede hangi entity üzerinde hangi aksiyonun yapıldığı izlenebilir.

## Kurulum

### 1. Projeyi klonla

```bash
git clone <repo-url>
cd financial-risk
```

### 2. Backend sanal ortamını oluştur ve aktif et

Windows:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Backend bağımlılıklarını kur

```powershell
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pandas numpy cryptography
```

### 4. `.env` dosyasını hazırla

Örnek:

```env
DATABASE_URL=postgresql://postgres@localhost:5432/financial_risk_db
APP_NAME=Financial Risk Management System
DEBUG=True
ENCRYPTION_KEY=buraya_fernet_key_yaz
```

Not:

- `ENCRYPTION_KEY` değeri Fernet formatında olmalıdır.
- Projede mevcut `.env` dosyası varsa onu kullanabilirsin.

### 5. Frontend bağımlılıklarını kur

```powershell
cd frontend
npm install
cd ..
```

## Çalıştırma

Bu projeyi en rahat 3 terminal ile çalıştırabilirsin.

### Terminal 1: PostgreSQL

PostgreSQL servisinin çalıştığından emin ol.

Örnek kontrol:

```powershell
psql -U postgres -d financial_risk_db
```

Eğer servis kapalıysa kendi PostgreSQL kurulumuna göre başlat:

```powershell
pg_ctl -D "<postgres-data-folder>" start
```

### Terminal 2: FastAPI

```powershell
cd C:\Users\PC\Documents\financial-risk
.\venv\Scripts\activate
uvicorn main:app --reload
```

Backend açıldıktan sonra:

- API root: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### Terminal 3: React

```powershell
cd C:\Users\PC\Documents\financial-risk\frontend
npm run dev
```

Frontend adresi:

- `http://127.0.0.1:5173`

## API Endpointleri

### Metal Endpointleri

- `GET /metals/prices`  
  Tüm metal fiyatlarını listeler.

- `GET /metals/prices/{metal_type}`  
  Belirli bir metalin fiyat kayıtlarını getirir.  
  Örnek: `XAU`, `XAG`

- `POST /metals/prices`  
  Yeni metal fiyatı ekler.

- `POST /metals/portfolio`  
  Portföy kaydı oluşturur.

- `POST /metals/simulate`  
  Portföy simülasyonu yapar.

- `GET /metals/var/{metal_type}`  
  Belirli bir metal için Historical VaR hesaplar.

### Customer Endpointleri

- `GET /customers`  
  Tüm müşterileri listeler.

- `POST /customers`  
  Yeni müşteri ekler.

- `GET /customers/{customer_id}`  
  Tek müşteri bilgisi getirir.

### Transaction Endpointleri

- `GET /transactions`  
  Tüm işlemleri listeler.

- `POST /transactions`  
  Yeni işlem ekler.

- `GET /transactions/customer/{customer_id}`  
  Belirli müşterinin işlemlerini getirir.

### Report Endpointleri

- `GET /reports/customer-summary`  
  Müşteri bazlı toplam yatırım ve işlem sayısını getirir.

- `GET /reports/metal-performance`  
  Altın ve gümüş toplam işlem hacmini karşılaştırır.

- `GET /reports/monthly-volume`  
  Aylık işlem hacmini döner.

- `POST /reports/compare-metals`  
  Aynı yatırım tutarını altın ve gümüşte karşılaştırır.

- `GET /reports/risk-summary/{customer_id}`  
  Müşteri bazlı toplam yatırım, güncel değer, kar/zarar ve VaR özetini getirir.

