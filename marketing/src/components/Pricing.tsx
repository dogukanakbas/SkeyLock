'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import Link from 'next/link';
import { CheckIcon } from '@heroicons/react/24/outline';

const tiers = [
  {
    name: 'Starter',
    id: 'starter',
    href: 'http://localhost:3000/register',
    price: { monthly: '$29', annually: '$290' },
    description: 'Perfect for small businesses and startups.',
    features: [
      'Up to 50 IoT devices',
      'Basic vulnerability scanning',
      'Email notifications',
      'Standard support',
      'Basic reporting',
      'API access',
    ],
    mostPopular: false,
  },
  {
    name: 'Professional',
    id: 'professional',
    href: 'http://localhost:3000/register',
    price: { monthly: '$99', annually: '$990' },
    description: 'Advanced features for growing organizations.',
    features: [
      'Unlimited IoT devices',
      'Advanced vulnerability scanning',
      'Real-time monitoring',
      'Priority support',
      'Advanced reporting & analytics',
      'Full API access',
      'Custom integrations',
      'Compliance templates',
    ],
    mostPopular: true,
  },
  {
    name: 'Enterprise',
    id: 'enterprise',
    href: '/contact',
    price: { monthly: '$299', annually: '$2990' },
    description: 'Comprehensive solution for large enterprises.',
    features: [
      'Everything in Professional',
      'Dedicated account manager',
      'Custom security policies',
      'On-premise deployment',
      'SSO integration',
      'Advanced threat intelligence',
      '24/7 phone support',
      'Custom training',
      'SLA guarantees',
    ],
    mostPopular: false,
  },
];

export default function Pricing() {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  return (
    <div id="pricing" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <motion.div
          ref={ref}
          className="mx-auto max-w-4xl text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-base font-semibold leading-7 text-blue-600">Pricing</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
            Choose the right plan for your organization
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Start with a 7-day free trial. No credit card required. Cancel anytime.
          </p>
        </motion.div>

        <div className="isolate mx-auto mt-16 grid max-w-md grid-cols-1 gap-y-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3 lg:gap-x-8 lg:gap-y-0">
          {tiers.map((tier, index) => (
            <motion.div
              key={tier.id}
              className={`flex flex-col justify-between rounded-3xl bg-white p-8 ring-1 ring-gray-200 xl:p-10 ${
                tier.mostPopular ? 'lg:z-10 lg:rounded-b-none' : 'lg:mt-8'
              }`}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
            >
              <div>
                <div className="flex items-center justify-between gap-x-4">
                  <h3
                    id={tier.id}
                    className={`text-lg font-semibold leading-8 ${
                      tier.mostPopular ? 'text-blue-600' : 'text-gray-900'
                    }`}
                  >
                    {tier.name}
                  </h3>
                  {tier.mostPopular ? (
                    <p className="rounded-full bg-blue-600/10 px-2.5 py-1 text-xs font-semibold leading-5 text-blue-600">
                      Most popular
                    </p>
                  ) : null}
                </div>
                <p className="mt-4 text-sm leading-6 text-gray-600">{tier.description}</p>
                <p className="mt-6 flex items-baseline gap-x-1">
                  <span className="text-4xl font-bold tracking-tight text-gray-900">
                    {tier.price.monthly}
                  </span>
                  <span className="text-sm font-semibold leading-6 text-gray-600">/month</span>
                </p>
                <ul role="list" className="mt-8 space-y-3 text-sm leading-6 text-gray-600">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex gap-x-3">
                      <CheckIcon
                        className="h-6 w-5 flex-none text-blue-600"
                        aria-hidden="true"
                      />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              <Link
                href={tier.name === 'Enterprise' ? '/contact' : '/iotsecurity-login'}
                aria-describedby={tier.id}
                className={`mt-8 block rounded-md px-3 py-2 text-center text-sm font-semibold leading-6 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
                  tier.mostPopular
                    ? 'bg-blue-600 text-white shadow-sm hover:bg-blue-500 focus-visible:outline-blue-600'
                    : 'text-blue-600 ring-1 ring-inset ring-blue-200 hover:ring-blue-300'
                }`}
              >
                {tier.name === 'Enterprise' ? 'Contact Sales' : 'Start Free Trial'}
              </Link>
            </motion.div>
          ))}
        </div>

        {/* FAQ Section */}
        <motion.div
          className="mt-24"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-12">
            Frequently Asked Questions
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                What happens during the free trial?
              </h4>
              <p className="text-gray-600 text-sm">
                You get full access to all Professional features for 7 days. No credit card required.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Can I change plans anytime?
              </h4>
              <p className="text-gray-600 text-sm">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Do you offer custom enterprise solutions?
              </h4>
              <p className="text-gray-600 text-sm">
                Yes, we provide custom solutions for large enterprises including on-premise deployment.
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                What kind of support do you provide?
              </h4>
              <p className="text-gray-600 text-sm">
                We offer email support for all plans, priority support for Professional, and 24/7 phone support for Enterprise.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}