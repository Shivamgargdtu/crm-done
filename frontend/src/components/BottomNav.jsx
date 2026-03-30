import React from 'react';
import { Link } from 'react-router-dom';
import { LayoutDashboard, Calendar, Table2, Users, Menu } from 'lucide-react';

const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    { icon: Calendar, label: 'Today', path: '/today' },
    { icon: Table2, label: 'Leads', path: '/leads' },
    { icon: Users, label: 'Team', path: '/team' },
];

export default function BottomNav({ counts, currentPath, onMenuClick }) {
    return (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 flex items-center justify-around py-2 pb-safe z-50 md:hidden">
            {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentPath === item.path || currentPath.startsWith(item.path);

                return (
                    <Link
                        key={item.path}
                        to={item.path}
                        data-testid={`bottom-nav-${item.label.toLowerCase()}`}
                        className={`flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-lg transition-colors ${
                            isActive 
                                ? 'text-[#E8536A]' 
                                : 'text-gray-500'
                        }`}
                    >
                        <Icon size={20} />
                        <span className="text-[10px] font-medium">{item.label}</span>
                    </Link>
                );
            })}
            <button
                onClick={onMenuClick}
                data-testid="bottom-nav-menu"
                className="flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-lg text-gray-500"
            >
                <Menu size={20} />
                <span className="text-[10px] font-medium">More</span>
            </button>
        </div>
    );
}
