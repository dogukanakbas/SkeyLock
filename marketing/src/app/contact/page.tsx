'use client';

import { useState } from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { EnvelopeIcon, PhoneIcon, MapPinIcon } from '@heroicons/react/24/outline';

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    message: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission here
    console.log('Form submitted:', formData);
    alert('Thank you for your message! We\'ll get back to you soon.');
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen bg-white">
      <Header />
      
      <div className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Contact Our Security Experts
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Ready to secure your IoT infrastructure? Get in touch with our team for a personalized demo 
              or to discuss your enterprise security needs.
            </p>
          </div>

          <div className="mx-auto mt-16 grid max-w-4xl grid-cols-1 gap-16 lg:grid-cols-2">
            {/* Contact Information */}
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Get in Touch</h2>
              <p className="mt-4 text-gray-600">
                Our security experts are here to help you protect your IoT infrastructure. 
                Reach out for enterprise solutions, technical support, or partnership opportunities.
              </p>

              <div className="mt-8 space-y-6">
                <div className="flex items-center">
                  <EnvelopeIcon className="h-6 w-6 text-blue-600" />
                  <span className="ml-3 text-gray-600">contact@cybersec-iot.com</span>
                </div>
                <div className="flex items-center">
                  <PhoneIcon className="h-6 w-6 text-blue-600" />
                  <span className="ml-3 text-gray-600">+1 (555) 123-4567</span>
                </div>
                <div className="flex items-center">
                  <MapPinIcon className="h-6 w-6 text-blue-600" />
                  <span className="ml-3 text-gray-600">San Francisco, CA</span>
                </div>
              </div>

              <div className="mt-12">
                <h3 className="text-lg font-semibold text-gray-900">Enterprise Sales</h3>
                <p className="mt-2 text-gray-600">
                  For organizations with 1000+ devices or custom deployment needs.
                </p>
                <a href="mailto:sales@cybersec-iot.com" className="mt-2 text-blue-600 hover:text-blue-500">
                  sales@cybersec-iot.com
                </a>
              </div>

              <div className="mt-8">
                <h3 className="text-lg font-semibold text-gray-900">Technical Support</h3>
                <p className="mt-2 text-gray-600">
                  Get help with implementation, integration, or troubleshooting.
                </p>
                <a href="mailto:support@cybersec-iot.com" className="mt-2 text-blue-600 hover:text-blue-500">
                  support@cybersec-iot.com
                </a>
              </div>
            </div>

            {/* Contact Form */}
            <div>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="name"
                    id="name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email Address
                  </label>
                  <input
                    type="email"
                    name="email"
                    id="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
                  />
                </div>

                <div>
                  <label htmlFor="company" className="block text-sm font-medium text-gray-700">
                    Company
                  </label>
                  <input
                    type="text"
                    name="company"
                    id="company"
                    value={formData.company}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
                  />
                </div>

                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700">
                    Message
                  </label>
                  <textarea
                    name="message"
                    id="message"
                    rows={4}
                    required
                    value={formData.message}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-3 py-2 border"
                    placeholder="Tell us about your IoT security needs..."
                  />
                </div>

                <button
                  type="submit"
                  className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                >
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}