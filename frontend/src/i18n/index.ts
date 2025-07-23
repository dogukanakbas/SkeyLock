import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translation resources
const resources = {
  en: {
    translation: {
      // Navigation
      'nav.features': 'Features',
      'nav.pricing': 'Pricing',
      'nav.demo': 'Demo',
      'nav.docs': 'Docs',
      'nav.contact': 'Contact',
      'nav.login': 'Log in',
      'nav.trial': 'Start Free Trial',
      
      // Hero Section
      'hero.title': 'Secure Your IoT Infrastructure with SkeyLock',
      'hero.subtitle': 'SkeyLock by Udar Soft - Enterprise-grade IoT security platform that automatically discovers, analyzes, and protects your connected devices with comprehensive vulnerability assessment and real-time monitoring.',
      'hero.cta': 'Start 7-Day Free Trial',
      'hero.demo': 'Watch Demo',
      'hero.discover': 'Discover',
      'hero.discover.desc': 'Automatically find all IoT devices on your network',
      'hero.analyze': 'Analyze',
      'hero.analyze.desc': 'Assess vulnerabilities and security risks instantly',
      'hero.protect': 'Protect',
      'hero.protect.desc': 'Monitor and secure your devices continuously',
      'hero.trial.note': 'No credit card required • 7-day free trial • Cancel anytime',
      
      // Auth
      'auth.register.title': 'Start Your 7-Day Free Trial',
      'auth.register.fullname': 'Full Name',
      'auth.register.company': 'Company Name',
      'auth.register.email': 'Work Email Address',
      'auth.register.phone': 'Phone Number',
      'auth.register.jobtitle': 'Job Title',
      'auth.register.password': 'Password (min 8 characters)',
      'auth.register.submit': 'Start Free Trial',
      'auth.register.creating': 'Creating Account...',
      'auth.register.login': 'Already have an account? Sign In',
      'auth.login.title': 'Sign In to SkeyLock',
      'auth.login.email': 'Email Address',
      'auth.login.password': 'Password',
      'auth.login.submit': 'Sign In',
      'auth.login.register': "Don't have an account? Start Free Trial",
      
      // Dashboard
      'dashboard.title': 'Dashboard',
      'dashboard.devices.total': 'Total Devices',
      'dashboard.devices.active': 'Active Devices',
      'dashboard.scans.total': 'Total Scans',
      'dashboard.issues.critical': 'Critical Issues',
      'dashboard.actions.title': 'Quick Actions',
      'dashboard.actions.add': 'Add New Device',
      'dashboard.actions.scan': 'Start Security Scan',
      'dashboard.subscription.title': 'Subscription Status',
      'dashboard.subscription.plan': 'Plan',
      'dashboard.subscription.status': 'Status',
      'dashboard.subscription.upgrade': 'Upgrade Plan',
      'dashboard.trial.warning': 'Your trial expires in {{days}} days. Upgrade to continue using all features.',
      'dashboard.trial.upgrade': 'Upgrade Now',
      
      // Pricing
      'pricing.trial.title': 'Trial',
      'pricing.trial.price': 'Free',
      'pricing.trial.desc': '7-day free trial with basic features',
      'pricing.starter.title': 'Starter',
      'pricing.starter.price': '$29/month',
      'pricing.starter.desc': 'Perfect for small businesses and startups',
      'pricing.professional.title': 'Professional',
      'pricing.professional.price': '$99/month',
      'pricing.professional.desc': 'Advanced features for growing organizations',
      'pricing.enterprise.title': 'Enterprise',
      'pricing.enterprise.price': '$299/month',
      'pricing.enterprise.desc': 'Comprehensive solution for large enterprises',
      
      // Navigation Menu
      'nav.devices': 'Devices',
      'nav.scans': 'Scans',
      'nav.analytics': 'Analytics',
      'nav.subscription': 'Subscription',
      'nav.admin': 'Admin Panel',
      'nav.logout': 'Logout',
      
      // Common
      'common.loading': 'Loading...',
      'common.error': 'Error',
      'common.success': 'Success',
      'common.cancel': 'Cancel',
      'common.save': 'Save',
      'common.delete': 'Delete',
      'common.edit': 'Edit',
      'common.add': 'Add',
      'common.search': 'Search',
      'common.filter': 'Filter',
      'common.export': 'Export',
      'common.import': 'Import',
    }
  },
  tr: {
    translation: {
      // Navigation
      'nav.features': 'Özellikler',
      'nav.pricing': 'Fiyatlandırma',
      'nav.demo': 'Demo',
      'nav.docs': 'Dokümantasyon',
      'nav.contact': 'İletişim',
      'nav.login': 'Giriş Yap',
      'nav.trial': 'Ücretsiz Deneme Başlat',
      
      // Hero Section
      'hero.title': 'IoT Altyapınızı SkeyLock ile Güvence Altına Alın',
      'hero.subtitle': 'Udar Soft tarafından geliştirilen SkeyLock - Bağlı cihazlarınızı otomatik olarak keşfeden, analiz eden ve kapsamlı güvenlik açığı değerlendirmesi ile gerçek zamanlı izleme sağlayan kurumsal düzeyde IoT güvenlik platformu.',
      'hero.cta': '7 Günlük Ücretsiz Deneme Başlat',
      'hero.demo': 'Demo İzle',
      'hero.discover': 'Keşfet',
      'hero.discover.desc': 'Ağınızdaki tüm IoT cihazları otomatik olarak bulun',
      'hero.analyze': 'Analiz Et',
      'hero.analyze.desc': 'Güvenlik açıklarını ve riskleri anında değerlendirin',
      'hero.protect': 'Koruyun',
      'hero.protect.desc': 'Cihazlarınızı sürekli izleyin ve güvence altına alın',
      'hero.trial.note': 'Kredi kartı gerekmez • 7 günlük ücretsiz deneme • İstediğiniz zaman iptal edin',
      
      // Auth
      'auth.register.title': '7 Günlük Ücretsiz Denemenizi Başlatın',
      'auth.register.fullname': 'Ad Soyad',
      'auth.register.company': 'Şirket Adı',
      'auth.register.email': 'İş E-posta Adresi',
      'auth.register.phone': 'Telefon Numarası',
      'auth.register.jobtitle': 'Pozisyon',
      'auth.register.password': 'Şifre (en az 8 karakter)',
      'auth.register.submit': 'Ücretsiz Deneme Başlat',
      'auth.register.creating': 'Hesap Oluşturuluyor...',
      'auth.register.login': 'Zaten hesabınız var mı? Giriş Yapın',
      'auth.login.title': 'SkeyLock\'a Giriş Yapın',
      'auth.login.email': 'E-posta Adresi',
      'auth.login.password': 'Şifre',
      'auth.login.submit': 'Giriş Yap',
      'auth.login.register': 'Hesabınız yok mu? Ücretsiz Deneme Başlatın',
      
      // Dashboard
      'dashboard.title': 'Kontrol Paneli',
      'dashboard.devices.total': 'Toplam Cihaz',
      'dashboard.devices.active': 'Aktif Cihaz',
      'dashboard.scans.total': 'Toplam Tarama',
      'dashboard.issues.critical': 'Kritik Sorun',
      'dashboard.actions.title': 'Hızlı İşlemler',
      'dashboard.actions.add': 'Yeni Cihaz Ekle',
      'dashboard.actions.scan': 'Güvenlik Taraması Başlat',
      'dashboard.subscription.title': 'Abonelik Durumu',
      'dashboard.subscription.plan': 'Plan',
      'dashboard.subscription.status': 'Durum',
      'dashboard.subscription.upgrade': 'Planı Yükselt',
      'dashboard.trial.warning': 'Deneme süreniz {{days}} gün içinde sona eriyor. Tüm özellikleri kullanmaya devam etmek için yükseltin.',
      'dashboard.trial.upgrade': 'Şimdi Yükselt',
      
      // Pricing
      'pricing.trial.title': 'Deneme',
      'pricing.trial.price': 'Ücretsiz',
      'pricing.trial.desc': 'Temel özelliklerle 7 günlük ücretsiz deneme',
      'pricing.starter.title': 'Başlangıç',
      'pricing.starter.price': '₺850/ay',
      'pricing.starter.desc': 'Küçük işletmeler ve girişimler için mükemmel',
      'pricing.professional.title': 'Profesyonel',
      'pricing.professional.price': '₺2.900/ay',
      'pricing.professional.desc': 'Büyüyen organizasyonlar için gelişmiş özellikler',
      'pricing.enterprise.title': 'Kurumsal',
      'pricing.enterprise.price': '₺8.750/ay',
      'pricing.enterprise.desc': 'Büyük kuruluşlar için kapsamlı çözüm',
      
      // Navigation Menu
      'nav.devices': 'Cihazlar',
      'nav.scans': 'Taramalar',
      'nav.analytics': 'Analitik',
      'nav.subscription': 'Abonelik',
      'nav.admin': 'Yönetici Paneli',
      'nav.logout': 'Çıkış Yap',
      
      // Common
      'common.loading': 'Yükleniyor...',
      'common.error': 'Hata',
      'common.success': 'Başarılı',
      'common.cancel': 'İptal',
      'common.save': 'Kaydet',
      'common.delete': 'Sil',
      'common.edit': 'Düzenle',
      'common.add': 'Ekle',
      'common.search': 'Ara',
      'common.filter': 'Filtrele',
      'common.export': 'Dışa Aktar',
      'common.import': 'İçe Aktar',
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,
    
    interpolation: {
      escapeValue: false,
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    }
  });

export default i18n;