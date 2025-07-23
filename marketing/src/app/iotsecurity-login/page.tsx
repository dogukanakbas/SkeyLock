'use client';

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  ShieldCheckIcon, 
  ArrowRightIcon, 
  CheckCircleIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  WifiIcon
} from '@heroicons/react/24/outline';

export default function IoTSecurityLogin() {
  // Auto-redirect after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      window.location.href = 'http://localhost:3000/login';
    }, 5000);

    return () => clearTimeout(timer);
  }, []);

  const features = [
    {
      icon: <DevicePhoneMobileIcon className="h-6 w-6" />,
      title: "Device Discovery",
      description: "Automatically find all IoT devices on your network"
    },
    {
      icon: <ShieldCheckIcon className="h-6 w-6" />,
      title: "Security Scanning",
      description: "Comprehensive vulnerability assessment and threat detection"
    },
    {
      icon: <ComputerDesktopIcon className="h-6 w-6" />,
      title: "Real-time Monitoring",
      description: "Continuous surveillance and instant threat alerts"
    },
    {
      icon: <WifiIcon className="h-6 w-6" />,
      title: "Network Analysis",
      description: "Deep network topology analysis and risk assessment"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <Link href="/" className="flex items-center space-x-2">
              <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">CyberSec IoT</span>
            </Link>
            <Link 
              href="/"
              className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-6">
            <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to IoT Security Platform
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            You're being redirected to our secure IoT security dashboard. 
            Get ready to protect your connected devices with enterprise-grade security.
          </p>

          {/* Redirect Notice */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8"
          >
            <div className="flex items-center justify-center mb-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="ml-3 text-blue-800 font-medium">Redirecting to IoT Security Dashboard...</span>
            </div>
            <p className="text-blue-700 text-sm">
              You will be automatically redirected in 5 seconds, or click the button below to continue immediately.
            </p>
          </motion.div>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <a
              href="http://localhost:3000/login"
              className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
            >
              Access IoT Security Dashboard
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </a>
          </motion.div>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
              className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
                    <div className="text-blue-600">
                      {feature.icon}
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Security Badges */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.2 }}
          className="bg-gray-50 rounded-lg p-8 text-center"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Enterprise-Grade Security
          </h3>
          <div className="flex flex-wrap justify-center items-center gap-6">
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-700">256-bit Encryption</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-700">SOC 2 Compliant</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-700">GDPR Ready</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-700">24/7 Monitoring</span>
            </div>
          </div>
        </motion.div>

        {/* Footer Note */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 1.5 }}
          className="text-center mt-12"
        >
          <p className="text-sm text-gray-500">
            Having trouble? <a href="/contact" className="text-blue-600 hover:text-blue-700">Contact our support team</a>
          </p>
        </motion.div>
      </div>
    </div>
  );
}