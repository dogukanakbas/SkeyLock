'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import Link from 'next/link';
import { PlayIcon, ComputerDesktopIcon, ShieldCheckIcon, ChartBarIcon } from '@heroicons/react/24/outline';

export default function Demo() {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  return (
    <div id="demo" className="py-24 sm:py-32 bg-gray-50">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          ref={ref}
          className="mx-auto max-w-2xl text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-base font-semibold leading-7 text-blue-600">
            See It In Action
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Experience CyberSec IoT Live
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Watch how our platform discovers, analyzes, and secures IoT devices in real-time. 
            See the power of automated vulnerability assessment.
          </p>
        </motion.div>

        {/* Demo Video Section */}
        <motion.div
          className="mx-auto mt-16 max-w-4xl"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="relative rounded-2xl bg-gray-900 p-2 shadow-2xl">
            <div className="relative aspect-video rounded-lg bg-gray-800 overflow-hidden">
              {/* Placeholder for demo video */}
              <div className="absolute inset-0 flex items-center justify-center">
                <button className="flex items-center justify-center w-20 h-20 bg-blue-600 rounded-full hover:bg-blue-500 transition-colors">
                  <PlayIcon className="h-8 w-8 text-white ml-1" />
                </button>
              </div>
              
              {/* Demo screenshot overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 to-purple-900/20">
                <div className="p-8 h-full flex flex-col justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-white text-sm ml-4">CyberSec IoT Dashboard</span>
                  </div>
                  
                  <div className="text-white">
                    <h3 className="text-2xl font-bold mb-2">Live IoT Security Dashboard</h3>
                    <p className="text-blue-200">Real-time device monitoring and threat detection</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Demo Features */}
        <motion.div
          className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            <div className="flex flex-col items-center text-center">
              <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                <div className="rounded-lg bg-blue-600 p-2">
                  <ComputerDesktopIcon className="h-5 w-5 text-white" aria-hidden="true" />
                </div>
                <span>Device Discovery</span>
              </dt>
              <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                <p className="flex-auto">
                  Watch as our platform automatically discovers and catalogs all IoT devices 
                  on your network in seconds.
                </p>
              </dd>
            </div>

            <div className="flex flex-col items-center text-center">
              <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                <div className="rounded-lg bg-blue-600 p-2">
                  <ShieldCheckIcon className="h-5 w-5 text-white" aria-hidden="true" />
                </div>
                <span>Vulnerability Scanning</span>
              </dt>
              <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                <p className="flex-auto">
                  See real-time vulnerability assessment with detailed risk scoring 
                  and remediation recommendations.
                </p>
              </dd>
            </div>

            <div className="flex flex-col items-center text-center">
              <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                <div className="rounded-lg bg-blue-600 p-2">
                  <ChartBarIcon className="h-5 w-5 text-white" aria-hidden="true" />
                </div>
                <span>Security Analytics</span>
              </dt>
              <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                <p className="flex-auto">
                  Explore comprehensive security analytics and compliance reporting 
                  with interactive dashboards.
                </p>
              </dd>
            </div>
          </dl>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          className="mx-auto mt-16 max-w-2xl text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to Secure Your IoT Infrastructure?
          </h3>
          <p className="text-gray-600 mb-8">
            Start your free 7-day trial and experience the power of automated IoT security.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/iotsecurity-login"
              className="rounded-md bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
              Start Free Trial
            </Link>
            <Link
              href="/contact"
              className="rounded-md border border-gray-300 px-6 py-3 text-sm font-semibold text-gray-900 shadow-sm hover:bg-gray-50"
            >
              Schedule Demo
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}