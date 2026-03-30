import React from 'react';
import { useLocation } from 'react-router-dom';
import { Construction } from 'lucide-react';

export default function PlaceholderPage({ title, description }) {
    const location = useLocation();
    const pageName = title || location.pathname.split('/').pop().replace(/-/g, ' ');

    return (
        <div className="flex flex-col items-center justify-center h-[60vh]" data-testid={`placeholder-${pageName.toLowerCase().replace(/\s+/g, '-')}`}>
            <div className="w-16 h-16 rounded-full bg-[#FFF5F5] flex items-center justify-center mb-4">
                <Construction size={28} className="text-[#E8536A]" />
            </div>
            <h1 className="font-heading text-xl font-semibold text-gray-900 capitalize">
                {pageName}
            </h1>
            <p className="text-[13px] text-gray-500 mt-2 text-center max-w-md">
                {description || 'This page is under construction. Check back soon!'}
            </p>
        </div>
    );
}
