import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, User, Phone, MapPin, Sprout, Lock, Mail } from 'lucide-react';
import { BioSniffLogo } from '../../components/common/BioSniffLogo';

export const SignUpPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: 'Ravi Kumar',
    phone: '98765 43210',
    email: 'ravi.kumar@gmail.com',
    state: 'Maharashtra',
    district: 'Ahmednagar',
    crop: 'Rice',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // After signup, direct to Farmer Overview as requested
    navigate('/farmer/overview');
  };

  return (
    <div className="min-h-screen bg-[#F6F9F6] flex flex-col justify-center py-10">
      <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
        <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-emerald-950/10 grid grid-cols-1 lg:grid-cols-12 min-h-[680px]">
          
          {/* Left Hero Graphic Banner */}
          <div className="lg:col-span-5 bg-[#0C2B1D] text-white p-8 sm:p-12 flex flex-col justify-between relative overflow-hidden">
            <div className="absolute inset-0 bg-radial from-emerald-600/20 via-transparent to-transparent pointer-events-none" />
            <img
              src="https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80"
              alt="Agricultural farmland"
              className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-30"
            />

            <div className="relative z-10">
              <Link to="/">
                <BioSniffLogo variant="light" size="lg" />
              </Link>
              <div className="mt-12 space-y-3">
                <span className="inline-block px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-xs font-semibold uppercase tracking-wider">
                  Join The Network
                </span>
                <h2 className="font-serif-display text-3xl sm:text-4xl font-bold text-white leading-tight">
                  Protect every acre with electronic precision.
                </h2>
                <p className="text-sm text-emerald-200/80 leading-relaxed">
                  Join over 12,000 progressive farmers safeguarding their crops from devastating pathogen outbreaks.
                </p>
              </div>
            </div>

            <div className="relative z-10 pt-8 space-y-3">
              <div className="flex items-center gap-3 text-xs text-emerald-200">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span>Zero hardware maintenance with solar nodes</span>
              </div>
              <div className="flex items-center gap-3 text-xs text-emerald-200">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span>Instant SMS & WhatsApp disease advisories</span>
              </div>
              <p className="font-handwritten text-xl text-emerald-200 leading-snug pt-2">
                “Healthy fields, brighter tomorrows.”
              </p>
            </div>
          </div>

          {/* Right Form */}
          <div className="lg:col-span-7 p-8 sm:p-12 flex flex-col justify-center">
            <div className="max-w-lg mx-auto w-full space-y-6">
              <div>
                <h3 className="font-serif-display text-3xl font-bold text-[#0F2D1F]">
                  Register Your Farm
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Create your profile to link with BIO-SNIFF node sensors.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                      Full Name
                    </label>
                    <div className="relative">
                      <User className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                        className="w-full pl-10 pr-3 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                      Mobile Number
                    </label>
                    <div className="relative">
                      <Phone className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
                      <input
                        type="text"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        required
                        className="w-full pl-10 pr-3 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      required
                      className="w-full pl-10 pr-3 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                      State
                    </label>
                    <div className="relative">
                      <MapPin className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
                      <select
                        value={formData.state}
                        onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                        className="w-full pl-10 pr-3 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                      >
                        <option>Maharashtra</option>
                        <option>Punjab</option>
                        <option>Uttar Pradesh</option>
                        <option>Madhya Pradesh</option>
                        <option>Karnataka</option>
                        <option>Tamil Nadu</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                      District / Taluka
                    </label>
                    <input
                      type="text"
                      value={formData.district}
                      onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                      className="w-full px-3.5 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                    Primary Crop
                  </label>
                  <div className="relative">
                    <Sprout className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
                    <select
                      value={formData.crop}
                      onChange={(e) => setFormData({ ...formData, crop: e.target.value })}
                      className="w-full pl-10 pr-3 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                    >
                      <option>Rice (Paddy)</option>
                      <option>Wheat</option>
                      <option>Cotton</option>
                      <option>Sugarcane</option>
                      <option>Maize</option>
                      <option>Soybean</option>
                    </select>
                  </div>
                </div>

                <div className="pt-2">
                  <label className="flex items-start gap-2 cursor-pointer text-xs text-gray-600">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500 mt-0.5"
                    />
                    <span>
                      I agree to the Terms of Service and consent to automated telemetry readings from my BIO-SNIFF field nodes.
                    </span>
                  </label>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 px-4 bg-[#0F3D2E] hover:bg-[#14523E] text-white font-semibold rounded-xl shadow-md transition-all flex items-center justify-center gap-2 text-sm mt-2"
                >
                  <span>Complete Registration & Open Farm</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </form>

              <div className="text-center pt-2 text-xs text-gray-500">
                Already registered?{' '}
                <Link to="/signin" className="font-semibold text-emerald-700 hover:underline">
                  Sign In to Dashboard
                </Link>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
