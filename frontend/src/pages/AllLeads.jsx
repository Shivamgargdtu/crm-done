import React, { useState, useEffect } from 'react';
import { useOutletContext, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { Search, Filter, ChevronDown, Phone, Mail, MapPin, User } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { ScrollArea } from '../components/ui/scroll-area';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORIES = [
    'Meeting Done', 'Interested', 'Call Back', 'Busy', 'No Response',
    'Foreign', 'Future Projection', 'Needs Review', 'Not Interested'
];

const PRIORITIES = ['Highest', 'High', 'Medium', 'Low', 'Review', 'Archive'];

const getCategoryStyle = (category) => {
    const styles = {
        'Meeting Done': 'bg-[#D1FAE5] text-[#065F46]',
        'Interested': 'bg-[#DBEAFE] text-[#1E40AF]',
        'Call Back': 'bg-[#FEF3C7] text-[#92400E]',
        'Busy': 'bg-[#FEE2E2] text-[#991B1B]',
        'No Response': 'bg-[#F3F4F6] text-[#374151]',
        'Foreign': 'bg-[#EDE9FE] text-[#5B21B6]',
        'Future Projection': 'bg-[#CCFBF1] text-[#115E59]',
        'Needs Review': 'bg-[#FFEDD5] text-[#9A3412]',
        'Not Interested': 'bg-[#E5E7EB] text-[#1F2937]'
    };
    return styles[category] || 'bg-gray-100 text-gray-600';
};

const getPriorityStyle = (priority) => {
    const styles = {
        'Highest': 'text-red-600',
        'High': 'text-orange-600',
        'Medium': 'text-yellow-600',
        'Low': 'text-green-600',
        'Review': 'text-blue-600',
        'Archive': 'text-gray-400'
    };
    return styles[priority] || 'text-gray-600';
};

export default function AllLeads() {
    const { counts } = useOutletContext();
    const [searchParams, setSearchParams] = useSearchParams();
    const [leads, setLeads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');
    const [priorityFilter, setPriorityFilter] = useState('');

    useEffect(() => {
        fetchLeads();
    }, [categoryFilter, priorityFilter, search]);

    const fetchLeads = async () => {
        try {
            const params = new URLSearchParams();
            if (categoryFilter) params.append('category', categoryFilter);
            if (priorityFilter) params.append('priority', priorityFilter);
            if (search) params.append('search', search);
            params.append('limit', '100');

            const response = await axios.get(`${API_URL}/api/leads?${params.toString()}`, {
                withCredentials: true
            });
            setLeads(response.data);
        } catch (err) {
            console.error('Error fetching leads:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        fetchLeads();
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 border-2 border-[#E8536A] border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-4 animate-fade-in" data-testid="all-leads-page">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="font-heading text-xl font-semibold text-gray-900">All Leads</h1>
                    <p className="text-[12px] text-gray-500 mt-0.5">{counts?.total || leads.length} total leads</p>
                </div>

                {/* Filters */}
                <div className="flex items-center gap-2 flex-wrap">
                    <form onSubmit={handleSearch} className="relative">
                        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                        <Input
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Search leads..."
                            className="pl-9 h-8 w-48 text-[12px] rounded-[8px]"
                            data-testid="search-leads-input"
                        />
                    </form>

                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" className="h-8 text-[12px] rounded-[8px]" data-testid="category-filter">
                                <Filter size={12} className="mr-1.5" />
                                {categoryFilter || 'Category'}
                                <ChevronDown size={12} className="ml-1.5" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => setCategoryFilter('')}>
                                All Categories
                            </DropdownMenuItem>
                            {CATEGORIES.map((cat) => (
                                <DropdownMenuItem key={cat} onClick={() => setCategoryFilter(cat)}>
                                    {cat}
                                </DropdownMenuItem>
                            ))}
                        </DropdownMenuContent>
                    </DropdownMenu>

                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" className="h-8 text-[12px] rounded-[8px]" data-testid="priority-filter">
                                {priorityFilter || 'Priority'}
                                <ChevronDown size={12} className="ml-1.5" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => setPriorityFilter('')}>
                                All Priorities
                            </DropdownMenuItem>
                            {PRIORITIES.map((pri) => (
                                <DropdownMenuItem key={pri} onClick={() => setPriorityFilter(pri)}>
                                    {pri}
                                </DropdownMenuItem>
                            ))}
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-[16px] shadow-[0_2px_12px_rgba(232,83,106,0.06)] border border-gray-100 overflow-hidden">
                <ScrollArea className="h-[calc(100vh-220px)]">
                    <table className="w-full compact-table" data-testid="leads-table">
                        <thead className="sticky top-0 bg-gray-50/95 backdrop-blur z-10">
                            <tr className="border-b border-gray-100">
                                <th className="px-3 py-2 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Company</th>
                                <th className="px-3 py-2 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Contact</th>
                                <th className="px-3 py-2 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Location</th>
                                <th className="px-3 py-2 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Category</th>
                                <th className="px-3 py-2 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Priority</th>
                                <th className="px-3 py-2 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Stage</th>
                                <th className="px-3 py-2 text-left text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Next Follow-up</th>
                            </tr>
                        </thead>
                        <tbody>
                            {leads.map((lead) => (
                                <tr 
                                    key={lead.id} 
                                    className="border-b border-gray-50 hover:bg-[#FFF5F5]/40 transition-colors cursor-pointer"
                                    data-testid={`lead-row-${lead.id}`}
                                >
                                    <td className="px-3 py-1.5">
                                        <span className="text-[13px] font-medium text-gray-900">{lead.companyName}</span>
                                    </td>
                                    <td className="px-3 py-1.5">
                                        <div className="flex flex-col gap-0.5">
                                            {lead.phone && (
                                                <span className="text-[12px] text-gray-600 flex items-center gap-1">
                                                    <Phone size={10} className="text-gray-400" />
                                                    {lead.phone}
                                                </span>
                                            )}
                                            {lead.email && (
                                                <span className="text-[12px] text-gray-500 flex items-center gap-1">
                                                    <Mail size={10} className="text-gray-400" />
                                                    {lead.email}
                                                </span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-3 py-1.5">
                                        <span className="text-[12px] text-gray-600 flex items-center gap-1">
                                            <MapPin size={10} className="text-gray-400" />
                                            {lead.city || '-'}{lead.state ? `, ${lead.state}` : ''}
                                        </span>
                                    </td>
                                    <td className="px-3 py-1.5">
                                        <span className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-medium ${getCategoryStyle(lead.category)}`}>
                                            {lead.category || '-'}
                                        </span>
                                    </td>
                                    <td className="px-3 py-1.5">
                                        <span className={`text-[12px] font-medium ${getPriorityStyle(lead.priority)}`}>
                                            {lead.priority || '-'}
                                        </span>
                                    </td>
                                    <td className="px-3 py-1.5">
                                        <span className="text-[12px] text-gray-600">{lead.pipelineStage || '-'}</span>
                                    </td>
                                    <td className="px-3 py-1.5">
                                        <span className="text-[12px] text-gray-500">
                                            {lead.nextFollowupDate ? new Date(lead.nextFollowupDate).toLocaleDateString() : '-'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {leads.length === 0 && (
                        <div className="text-center py-12">
                            <User size={40} className="mx-auto text-gray-300 mb-3" />
                            <p className="text-[13px] text-gray-500">No leads found</p>
                            <p className="text-[12px] text-gray-400 mt-1">Import leads to get started</p>
                        </div>
                    )}
                </ScrollArea>
            </div>
        </div>
    );
}
