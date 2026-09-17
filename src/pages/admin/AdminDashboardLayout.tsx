import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { AdminSidebar } from '../../components/common/AdminSidebar';
import { Bell, Search, UserCheck, LogOut, ChevronDown, Sprout } from 'lucide-react';

export const AdminDashboardLayout: React.FC = () => {
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = React.useState(false);

  return (
    <div className="min-h-screen bg-[#F6F9F6] text-[#1A281E] flex font-sans">
      {/* Admin Sidebar */}
      <AdminSidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200/90 px-6 py-3.5 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-950">
                  National Agricultural Grid
                </span>
              </div>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-gray-100 text-gray-700 font-semibold hidden sm:inline-block">
                Region: All India (28 States)
              </span>
            </div>

            <div className="flex items-center gap-4">
              <Link
                to="/farmer/overview"
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-100/70 text-emerald-900 text-xs font-bold hover:bg-emerald-200 transition"
              >
                <Sprout className="w-3.5 h-3.5 text-emerald-700" />
                <span>Switch to Farmer View</span>
              </Link>

              <button
                onClick={() => alert('12 Active Network Alerts: 2 Critical, 4 High, 6 Medium.')}
                className="relative p-2 text-gray-500 hover:text-gray-800 rounded-lg hover:bg-gray-100"
              >
                <Bell className="w-4 h-4" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
              </button>

              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2.5 p-1 rounded-xl hover:bg-gray-100 transition"
                >
                  <img
                    src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&q=80"
                    alt="Admin Avatar"
                    className="w-8 h-8 rounded-full object-cover border border-emerald-300"
                  />
                  <div className="hidden sm:block text-left text-xs">
                    <span className="font-bold text-gray-900 block leading-tight">Admin Console</span>
                    <span className="text-[10px] text-gray-500 leading-tight">ICAR-Central Node</span>
                  </div>
                  <ChevronDown className="w-3 h-3 text-gray-400" />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-48 rounded-xl border border-gray-200 bg-white py-1.5 shadow-xl z-50 text-xs">
                    <div className="px-3.5 py-2 border-b border-gray-100">
                      <p className="font-bold text-gray-900">Dr. Sunita Rao</p>
                      <p className="text-gray-500 text-[11px]">System Super-Admin</p>
                    </div>
                    <Link
                      to="/admin/overview"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-gray-700 hover:bg-gray-50"
                    >
                      Admin Overview
                    </Link>
                    <Link
                      to="/admin/farmers"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-gray-700 hover:bg-gray-50"
                    >
                      Farmers Directory
                    </Link>
                    <Link
                      to="/farmer/overview"
                      onClick={() => setProfileOpen(false)}
                      className="block px-3.5 py-2 text-emerald-700 font-semibold hover:bg-emerald-50"
                    >
                      View Farmer Farm
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

        {/* Dynamic Nested Content */}
        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
