# 🌐 SkeyLock Türkçe Dil Desteği Rehberi

## 📍 Dil Değiştirme Yerleri

### **1. Web Uygulamasında (Frontend)**
**Konum**: Ana uygulama içinde, üst menü çubuğunda
- Layout component'inde LanguageSwitcher bulunuyor
- Dil seçenekleri: 🇺🇸 English | 🇹🇷 Türkçe
- Seçilen dil localStorage'da saklanıyor

### **2. Marketing Site'de**
**Konum**: Ana sayfa header'ında
- Header component'inde dil butonları var
- Basit buton formatında: EN | TR

## 🔧 Dil Değiştirme Nasıl Çalışır?

### **Otomatik Dil Algılama**
```javascript
// Tarayıcı dilini otomatik algılar
// Türkçe tarayıcı → Türkçe interface
// İngilizce tarayıcı → İngilizce interface
```

### **Manuel Dil Değiştirme**
1. **Web App'te**: Üst menüde dil değiştirici ikonuna tıkla
2. **Marketing'te**: Header'da EN/TR butonlarına tıkla
3. **Seçim**: Dropdown'dan istediğin dili seç
4. **Kayıt**: Seçim otomatik kaydedilir

## 📝 Çeviri Kapsamı

### **Tam Çevrilmiş Bölümler**
✅ **Navigation Menu**
- Dashboard → Kontrol Paneli
- Devices → Cihazlar  
- Scans → Taramalar
- Analytics → Analitik
- Subscription → Abonelik

✅ **Auth Pages**
- Login → Giriş Yap
- Register → Kayıt Ol
- "Start Free Trial" → "Ücretsiz Deneme Başlat"

✅ **Dashboard**
- "Total Devices" → "Toplam Cihaz"
- "Active Devices" → "Aktif Cihaz"
- "Critical Issues" → "Kritik Sorun"

✅ **Pricing**
- Trial → Deneme (Ücretsiz)
- Starter → Başlangıç (₺850/ay)
- Professional → Profesyonel (₺2.900/ay)
- Enterprise → Kurumsal (₺8.750/ay)

## 💰 Türkçe Fiyatlandırma

### **TL Cinsinden Fiyatlar**
- **Deneme**: Ücretsiz (7 gün)
- **Başlangıç**: ₺850/ay (50 cihaz)
- **Profesyonel**: ₺2.900/ay (500 cihaz)
- **Kurumsal**: ₺8.750/ay (sınırsız)

### **Özellik Açıklamaları**
- "Perfect for small businesses" → "Küçük işletmeler için mükemmel"
- "Advanced features" → "Gelişmiş özellikler"
- "Comprehensive solution" → "Kapsamlı çözüm"

## 🎯 Kullanım Talimatları

### **1. İlk Kez Kullanım**
```bash
# Frontend'i başlat
cd frontend
npm install
npm start

# Tarayıcıda aç: http://localhost:3000
# Üst menüde dil değiştirici görünecek
```

### **2. Dil Değiştirme**
1. **Uygulama içinde**: Sağ üst köşede dil ikonu
2. **Tıkla**: Dropdown menü açılır
3. **Seç**: 🇹🇷 Türkçe'yi seç
4. **Otomatik**: Sayfa Türkçe'ye çevrilir

### **3. Kalıcı Ayar**
- Seçilen dil localStorage'da saklanır
- Bir sonraki ziyarette aynı dil açılır
- Tarayıcı temizlenene kadar kalır

## 🔧 Geliştirici Notları

### **Yeni Çeviri Ekleme**
```typescript
// frontend/src/i18n/index.ts dosyasında
const resources = {
  en: {
    translation: {
      'new.key': 'English Text'
    }
  },
  tr: {
    translation: {
      'new.key': 'Türkçe Metin'
    }
  }
};
```

### **Component'te Kullanım**
```typescript
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();
  
  return (
    <h1>{t('new.key')}</h1>
  );
};
```

### **Dinamik Çeviri**
```typescript
// Değişken ile çeviri
t('dashboard.trial.warning', { days: 5 })
// Çıktı: "Deneme süreniz 5 gün içinde sona eriyor."
```

## 🎨 UI/UX Notları

### **Dil Değiştirici Tasarımı**
- **Bayrak İkonları**: 🇺🇸 🇹🇷 görsel tanıma
- **Dropdown Menu**: Material-UI styled
- **Hover Effect**: Mavi renk geçişi
- **Active State**: Seçili dil vurgulanır

### **Responsive Tasarım**
- **Desktop**: Dropdown menu
- **Mobile**: Basit buton listesi
- **Tablet**: Orta boyut dropdown

## 📱 Test Etme

### **Dil Değiştirme Testi**
1. Uygulamayı aç
2. İngilizce olarak başladığını kontrol et
3. Dil değiştiriciyi bul
4. Türkçe'ye geç
5. Tüm metinlerin çevrildiğini kontrol et

### **Kalıcılık Testi**
1. Türkçe'ye geç
2. Sayfayı yenile (F5)
3. Türkçe olarak açıldığını kontrol et
4. Tarayıcıyı kapat/aç
5. Hala Türkçe olduğunu kontrol et

## 🚀 Production'da Kullanım

### **Deployment Sonrası**
- Dil desteği otomatik aktif
- Kullanıcılar hemen kullanabilir
- Ek konfigürasyon gerekmez

### **SEO Optimizasyonu**
- Türkçe meta taglar eklendi
- Dil alternatifleri belirtildi
- Google'da iki dilde indekslenecek

---

## 🎉 Özet

**SkeyLock by Udar Soft** artık tam Türkçe dil desteği ile geliyor!

**Kullanım**: Üst menüdeki 🇹🇷 TR butonuna tıkla
**Kapsam**: Tüm arayüz Türkçe
**Fiyatlar**: Türk Lirası cinsinden
**Kalıcı**: Seçim kaydediliyor

Türk kullanıcılar için tamamen yerelleştirilmiş deneyim! 🇹🇷