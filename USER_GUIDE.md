# 🚀 SkeyLock by Udar Soft - Kullanıcı Rehberi

## 📋 Platform Genel Bakış

SkeyLock, Udar Soft tarafından geliştirilen, işletmelerin IoT cihazlarını otomatik olarak keşfeden, analiz eden ve güvenlik açıklarını tespit eden enterprise seviyede bir SaaS platformudur.

## 🌐 Platform Mimarisi

### 1. **Marketing Website** (yourdomain.com)
- **Amaç**: Müşteri kazanımı ve bilgilendirme
- **Özellikler**:
  - Modern landing page
  - Ürün özellikleri ve fiyatlandırma
  - Demo videoları
  - Ücretsiz deneme kayıt formu
  - İletişim sayfası

### 2. **Web Application** (app.yourdomain.com)
- **Amaç**: Ana kullanıcı arayüzü
- **Özellikler**:
  - Dashboard ve analytics
  - Cihaz yönetimi
  - Tarama geçmişi
  - Abonelik yönetimi
  - Admin paneli

### 3. **API Backend** (api.yourdomain.com)
- **Amaç**: Tüm backend işlemleri
- **Özellikler**:
  - RESTful API
  - Authentication & Authorization
  - Database operations
  - Background tasks
  - Webhook endpoints

## 👥 Kullanıcı Deneyimi Akışı

### 🎯 **1. Müşteri Keşif Süreci**

#### A) Marketing Site Ziyareti
```
yourdomain.com → Hero Section → Features → Pricing → Free Trial
```

**Kullanıcı Görür:**
- "Secure Your IoT Infrastructure in Minutes"
- 3 ana özellik: Discover, Analyze, Protect
- Fiyatlandırma planları
- "Start 7-Day Free Trial" butonu

#### B) Kayıt Süreci
```
Free Trial Click → app.yourdomain.com/register → Form Doldur → Email Doğrulama
```

**Kayıt Formu:**
- Email adresi
- Şirket adı
- Tam ad
- Güçlü şifre
- Şartları kabul

### 🏢 **2. İlk Giriş ve Onboarding**

#### A) Dashboard İlk Görünüm
```javascript
// Kullanıcı ilk girişte görür:
{
  "total_devices": 0,
  "active_devices": 0,
  "total_scans": 0,
  "critical_vulnerabilities": 0,
  "subscription_plan": "trial",
  "trial_days_left": 7
}
```

#### B) Hızlı Başlangıç Adımları
1. **"Add First Device"** butonu
2. **Network Discovery** özelliği
3. **Quick Scan** başlatma
4. **Results** görüntüleme

### 🔍 **3. Ana Kullanım Senaryoları**

#### **Senaryo A: IT Yöneticisi - Ağ Keşfi**

```
1. Dashboard → "Discover Network" 
2. IP Range gir (192.168.1.0/24)
3. Otomatik tarama başlar
4. Bulunan cihazlar listelenir
5. Her cihaz için detay görüntülenir
```

**Kullanıcı Görür:**
- IP adresi: 192.168.1.100
- Hostname: smart-camera-01
- Device Type: IP Camera
- Manufacturer: Hikvision
- Open Ports: 80, 554, 8000
- Risk Score: 8.5/10 (High)

#### **Senaryo B: Güvenlik Uzmanı - Vulnerability Assessment**

```
1. Devices → Select Device → "Full Security Scan"
2. Tarama türü seç: Vulnerability Scan
3. Background'da Celery task çalışır
4. Real-time progress gösterilir
5. Detaylı rapor oluşturulur
```

**Rapor İçeriği:**
```json
{
  "device_id": 123,
  "scan_type": "vulnerability",
  "vulnerabilities": [
    {
      "cve_id": "CVE-2023-1234",
      "severity": "critical",
      "description": "Default credentials vulnerability",
      "solution": "Change default password"
    }
  ],
  "risk_score": 9.2,
  "recommendations": [...]
}
```

#### **Senaryo C: Yönetici - Abonelik Yönetimi**

```
1. Trial 7. gün → Warning notification
2. Subscription → Plan seç (Starter $29/ay)
3. Stripe payment form
4. Ödeme tamamlandı → Plan upgrade
5. Yeni limitler aktif
```

## 🔧 Teknik Çalışma Mantığı

### **1. Multi-Tenant Architecture**

```python
# Her müşteri ayrı tenant
class Tenant(Base):
    id = Column(String, primary_key=True)
    name = Column(String)
    plan_type = Column(String)  # trial, starter, professional
    max_devices = Column(Integer)
    max_scans_per_month = Column(Integer)
```

**Veri İzolasyonu:**
- Her API call'da tenant_id kontrolü
- Database'de tenant_id ile filtreleme
- Subdomain-based routing

### **2. Background Processing**

```python
# Celery Tasks
@celery_app.task
def perform_device_scan(device_id, scan_type, tenant_id):
    # 1. Device bilgilerini al
    # 2. Nmap ile port tarama
    # 3. Service detection
    # 4. Vulnerability database sorgusu
    # 5. Risk score hesaplama
    # 6. Sonuçları kaydet
    # 7. Email notification gönder
```

**Task Queues:**
- `scanning`: Cihaz taramaları
- `notifications`: Email/SMS gönderimi
- `billing`: Ödeme işlemleri
- `maintenance`: Sistem bakımı

### **3. Real-time Updates**

```javascript
// Frontend WebSocket connection
const ws = new WebSocket('wss://api.yourdomain.com/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'scan_progress') {
    updateScanProgress(data.progress);
  }
};
```

## 💰 Monetization Akışı

### **1. Freemium Model**

```
Trial (7 gün) → Starter ($29/ay) → Professional ($99/ay) → Enterprise ($299/ay)
```

**Limit Kontrolü:**
```python
def check_device_limit(tenant_id):
    tenant = get_tenant(tenant_id)
    device_count = count_devices(tenant_id)
    
    limits = {
        'trial': 5,
        'starter': 50,
        'professional': 500,
        'enterprise': -1  # unlimited
    }
    
    return device_count < limits[tenant.plan_type]
```

### **2. Usage-Based Billing**

```python
# Aylık kullanım takibi
@celery_app.task
def process_monthly_billing():
    for tenant in get_all_tenants():
        usage = calculate_usage(tenant.id)
        if usage.exceeds_plan_limits():
            send_upgrade_notification(tenant)
```

## 📊 Kullanıcı Metrikleri

### **1. Onboarding Funnel**
```
Marketing Site Visit → 100%
Free Trial Signup → 15%
First Device Added → 60%
First Scan Completed → 80%
Paid Conversion → 25%
```

### **2. Engagement Metrics**
```
Daily Active Users (DAU)
Weekly Scans per User
Average Session Duration
Feature Adoption Rate
Churn Rate by Plan
```

## 🎯 Kullanım Örnekleri

### **Küçük İşletme (Starter Plan)**
- 20 IP kamera
- 10 akıllı termostat
- 5 network printer
- Haftalık otomatik tarama
- Email raporları

### **Orta Ölçekli Şirket (Professional Plan)**
- 200 IoT sensör
- 50 endüstriyel cihaz
- 100 network device
- Günlük tarama
- Real-time monitoring
- API entegrasyonu

### **Enterprise (Enterprise Plan)**
- 1000+ cihaz
- Çoklu lokasyon
- Custom security policies
- Dedicated support
- On-premise deployment

## 🚀 Başarı Faktörleri

### **1. Kolay Onboarding**
- 5 dakikada ilk tarama
- Otomatik cihaz keşfi
- Anlaşılır dashboard

### **2. Değer Kanıtlama**
- İlk taramada kritik açık bulma
- Risk score ile somut metrik
- Actionable recommendations

### **3. Sticky Features**
- Scheduled scans
- Email alerts
- Compliance reports
- API integrations

SkeyLock by Udar Soft, IoT güvenliği alanında gerçek bir ihtiyacı karşılayan, kullanıcı dostu ve ölçeklenebilir bir SaaS çözümüdür! 🎉