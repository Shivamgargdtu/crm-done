import React from 'react';
import { Search, X } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import {
    Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from './ui/select';

const CATEGORIES = [
    'Meeting Done', 'Interested', 'Call Back', 'Busy', 'No Response',
    'Foreign', 'Future Projection', 'Needs Review', 'Not Interested'
];
const PRIORITIES = ['Highest', 'High', 'Medium', 'Low', 'Review', 'Archive'];

export function LeadFilterBar({
    search, onSearchChange,
    categoryFilter, onCategoryChange,
    priorityFilter, onPriorityChange,
    assignedToFilter, onAssignedToChange,
    cityFilter, onCityChange,
    portfolioSentFilter, onPortfolioSentChange,
    showDuplicatesOnly, onDuplicatesChange,
    chattingViaFilter, onChattingViaChange,
    hasFilters, onClearFilters,
    teamMembers, cities
}) {
    return (
        <div className="flex items-center gap-2 flex-wrap">
            <div className="relative flex-1 min-w-[180px] max-w-[240px]">
                <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
                <Input
                    value={search}
                    onChange={(e) => onSearchChange(e.target.value)}
                    placeholder="Search company, name, phone, city..."
                    className="pl-8 h-8 text-[11px] rounded-[8px]"
                    data-testid="search-leads-input"
                />
            </div>

            <Select value={categoryFilter || undefined} onValueChange={(v) => onCategoryChange(v === '_all_' ? '' : v)}>
                <SelectTrigger className="w-[130px] h-8 text-[11px] rounded-[8px]" data-testid="category-filter">
                    <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="_all_">All Categories</SelectItem>
                    {CATEGORIES.map(cat => (
                        <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                    ))}
                </SelectContent>
            </Select>

            <Select value={priorityFilter || undefined} onValueChange={(v) => onPriorityChange(v === '_all_' ? '' : v)}>
                <SelectTrigger className="w-[100px] h-8 text-[11px] rounded-[8px]" data-testid="priority-filter">
                    <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="_all_">All</SelectItem>
                    {PRIORITIES.map(p => (
                        <SelectItem key={p} value={p}>{p}</SelectItem>
                    ))}
                </SelectContent>
            </Select>

            <Select value={assignedToFilter || undefined} onValueChange={(v) => onAssignedToChange(v === '_all_' ? '' : v)}>
                <SelectTrigger className="w-[120px] h-8 text-[11px] rounded-[8px]" data-testid="assigned-filter">
                    <SelectValue placeholder="Assigned To" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="_all_">All</SelectItem>
                    {teamMembers.map(m => (
                        <SelectItem key={m.id} value={m.id}>{m.name}</SelectItem>
                    ))}
                </SelectContent>
            </Select>

            <Select value={cityFilter || undefined} onValueChange={(v) => onCityChange(v === '_all_' ? '' : v)}>
                <SelectTrigger className="w-[100px] h-8 text-[11px] rounded-[8px]">
                    <SelectValue placeholder="City" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="_all_">All Cities</SelectItem>
                    {cities.map(c => (
                        <SelectItem key={c} value={c}>{c}</SelectItem>
                    ))}
                </SelectContent>
            </Select>

            <Select value={portfolioSentFilter || undefined} onValueChange={(v) => onPortfolioSentChange(v === '_all_' ? '' : v)}>
                <SelectTrigger className="w-[110px] h-8 text-[11px] rounded-[8px]">
                    <SelectValue placeholder="Portfolio" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="_all_">All</SelectItem>
                    <SelectItem value="yes">Sent</SelectItem>
                    <SelectItem value="no">Not Sent</SelectItem>
                </SelectContent>
            </Select>

            <label className="flex items-center gap-1.5 text-[11px] text-gray-600 cursor-pointer">
                <Checkbox
                    checked={showDuplicatesOnly}
                    onCheckedChange={onDuplicatesChange}
                    className="h-4 w-4"
                />
                Duplicates
            </label>

            <Select value={chattingViaFilter || 'all'} onValueChange={v => onChattingViaChange(v === 'all' ? '' : v)}>
                <SelectTrigger className="w-[120px] h-8 text-[11px] rounded-[8px]" data-testid="filter-chatting-via">
                    <SelectValue placeholder="Chatting Via" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="all">All Numbers</SelectItem>
                    <SelectItem value="5235">...5235</SelectItem>
                    <SelectItem value="5533">...5533</SelectItem>
                    <SelectItem value="0951">...0951</SelectItem>
                </SelectContent>
            </Select>

            {hasFilters && (
                <Button
                    onClick={onClearFilters}
                    variant="ghost"
                    className="h-8 text-[11px] text-[#E8536A] hover:text-[#D43D54]"
                >
                    <X size={12} className="mr-1" />
                    Clear
                </Button>
            )}
        </div>
    );
}
