import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { FarmerSidebar } from '../../components/common/FarmerSidebar';
import { Bell, ShieldCheck, ChevronDown, LogOut, ArrowLeft } from 'lucide-react';

export const FarmerDashboardLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [profileOpen, setProfileOpen] = React.useState(false);

  return (
    <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex font-sans">
      {/* Farmer Sidebar (Appears after Inspect Bio-Sniff) */}
      <FarmerSidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Top bar inside the dashboard */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200/90 px-6 py-3 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link
                to="/farmer/overview"
                className="flex items-center gap-1.5 text-xs font-semibold text-gray-600 hover:text-emerald-800 bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg transition"
                title="Back to Farm Overview Map"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Farm Map</span>
              </Link>
              <div className="h-4 w-px bg-gray-200" />
              <div className="text-xs text-gray-500 font-medium">
                Farm: <strong className="text-gray-900">Ravi Agro Fields (Ahmednagar)</strong>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Link
                to="/admin/overview"
                className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-900 text-emerald-100 text-xs font-medium hover:bg-emerald-800 transition"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Admin View</span>
              </Link>

              <button
                onClick={() => alert('Sensors synced: 06:42 AM IST')}
                className="relative p-2 text-gray-500 hover:text-gray-800 rounded-lg hover:bg-gray-100"
              >
                <Bell className="w-4 h-4" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full" />
              </button>

              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2.5 p-1 rounded-xl hover:bg-gray-100 transition"
                >
                  <img
                    src="https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=100&q=80"
                    alt="Ravi Kumar"
                    className="w-8 h-8 rounded-full object-cover border border-emerald-300"
                  />
                  <div className="hidden sm:block text-left text-xs">
                    <span className="font-bold text-gray-900 block leading-tight">Ravi Kumar</span>
                    <span className="text-[10px] text-gray-500 leading-tight">Farmer</span>
                  </div>
                  <ChevronDown className="w-3 h-3 text-gray-400" />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-48 rounded-xl border border-gray-200 bg-white py-1.5 shadow-xl z-50 text-xs">
                    <Link
                      to="/farmer/overview"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-gray-700 hover:bg-gray-50"
                    >
                      Farmer Overview
                    </Link>
                    <Link
                      to="/farmer/system"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-gray-700 hover:bg-gray-50"
                    >
                      System Telemetry
                    </Link>
                    <Link
                      to="/admin/overview"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-emerald-700 font-semibold hover:bg-emerald-50"
                    >
                      Admin Network
                    </Link>
                    <div className="border-t border-gray-100 my-1" />
                    <button
                      onClick={() => navigate('/signin')}
                      className="flex items-center gap-2 w-full text-left px-3.5 py-2 text-red-600 hover:bg-red-50"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>Log Out</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Nested Route Content */}
        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
