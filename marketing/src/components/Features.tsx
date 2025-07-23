'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import {
  MagnifyingGlassIcon,
  ShieldExclamationIcon,
  ClockIcon,
  DocumentChartBarIcon,
  BellAlertIcon,
  CogIcon,
  GlobeAltIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';

const features = [
  {
    name: 'Automated Device Discovery',
    description: 'Automatically scan and identify all IoT devices on your network with detailed fingerprinting and classification.',
    icon: MagnifyingGlassIcon,
  },
  {
    name: 'Vulnerability Assessment',
    description: 'Comprehensive security analysis using industry-standard CVE databases and custom threat intelligence.',
    icon: ShieldExclamationIcon,
  },
  {
    name: 'Real-time Monitoring',
    description: 'Continuous surveillance of your IoT infrastructure with instant threat detection and response.',
    icon: ClockIcon,
  },
  {
    name: 'Compliance Reporting',
    description: 'Generate detailed reports for GDPR, HIPAA, SOX, and other regulatory compliance requirements.',
    icon: DocumentChartBarIcon,
  },
  {
    name: 'Instant Alerts',
    description: 'Get notified immediately when new threats are detected via email, SMS, or webhook integrations.',
    icon: BellAlertIcon,
  },
  {
    name: 'Easy Integration',
    description: 'Seamlessly integrate with existing security tools and SIEM platforms through our REST API.',
    icon: CogIcon,
  },
  {
    name: 'Global Threat Intelligence',
    description: 'Access to real-time threat feeds and security intelligence from our global network.',
    icon: GlobeAltIcon,
  },
  {
    name: 'Multi-tenant Management',
    description: 'Manage multiple organizations and teams with role-based access control and permissions.',
    icon: UserGroupIcon,
  },
];

export default function Features() {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  return (
    <div id="features" className="py-24 sm:py-32 bg-gray-50">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          ref={ref}
          className="mx-auto max-w-2xl text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-base font-semibold leading-7 text-blue-600">
            Comprehensive Security
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Everything you need to secure your IoT infrastructure
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Our platform provides enterprise-grade security features designed specifically 
            for IoT environments, from discovery to protection.
          </p>
        </motion.div>

        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-2">
            {features.map((feature, index) => (
              <motion.div
                key={feature.name}
                className="flex flex-col"
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
              >
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                  <div className="rounded-lg bg-blue-600 p-2">
                    <feature.icon className="h-5 w-5 text-white" aria-hidden="true" />
                  </div>
                  {feature.name}
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">{feature.description}</p>
                </dd>
              </motion.div>
            ))}
          </dl>
        </div>

        {/* Stats Section */}
        <motion.div
          className="mt-24 bg-white rounded-2xl shadow-lg p-8 lg:p-12"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">99.9%</div>
              <div className="text-sm text-gray-600">Uptime SLA</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">10M+</div>
              <div className="text-sm text-gray-600">Devices Scanned</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">500+</div>
              <div className="text-sm text-gray-600">Enterprise Customers</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">24/7</div>
              <div className="text-sm text-gray-600">Expert Support</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}