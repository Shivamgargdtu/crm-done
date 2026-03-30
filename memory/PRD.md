# Wed Us CRM - Product Requirements Document

## Original Problem Statement
Build a CRM web app called "Wed Us CRM" for a wedding design company with:
- FastAPI backend (Python) + React frontend + MongoDB
- JWT authentication with Admin/Team Member roles
- Default admin: admin@wedus.com / admin123
- Sidebar navigation with live count badges
- Dashboard with stat cards
- All leads table with category/priority filters
- Team management
- Design: #FFF5F5 background, #E8536A coral pink accent, Poppins/Inter fonts
- Compact data-dense layout for maximum visibility
- Mobile responsive with bottom navigation

## User Personas
1. **Admin** - Full access to all leads, team management, settings
2. **Team Member** - Access only to assigned leads, cannot add team members

## Core Requirements (Static)
### Authentication
- JWT-based email/password login
- Role-based access control (admin/team_member)
- Protected routes with redirect to login
- Cookie-based token storage with httpOnly

### Database Schema - Leads
Required fields: companyName, phone, phone2, whatsapp, whatsapp2, primaryWhatsapp, instagram, email, city, address, state, status, category, categoryRank, priority, priorityRank, pipelineStage, assignedTo, sourceSheet, nextFollowupDate, lastContactDate, dateAdded, dateMarkedNotInterested, portfolioSent, priceListSent, waSent, responseHistory[], mostCommonResponse, mostCommonResponseRank, isDuplicate, duplicateOf, duplicateDismissed, notes, callCount

### Categories (with ranks)
1. Meeting Done, 2. Interested, 3. Call Back, 4. Busy, 5. No Response, 6. Foreign, 7. Future Projection, 8. Needs Review, 9. Not Interested

### Pipeline Stages
New Contact, Interested, Send Portfolio, Time Given, Meeting Scheduled, Meeting Done, Project Follow-up, Onboarded, Unknown, Call Again 1-3, Not Answering, Not Interested

### Priorities
1. Highest, 2. High, 3. Medium, 4. Low, 5. Review, 6. Archive

## What's Been Implemented (Phase 1 - 2026-03-30)
- ✅ FastAPI backend with all lead/team/auth endpoints
- ✅ JWT authentication with cookie-based tokens
- ✅ MongoDB models for users and leads with proper indexes
- ✅ Admin seeding (admin@wedus.com / admin123)
- ✅ Sample team members (Priya Sharma, Rahul Mehta, Ananya Singh - password: team123)
- ✅ React frontend with all routes
- ✅ Login page with validation
- ✅ Dashboard with stat cards and category/pipeline overview
- ✅ Sidebar with all navigation items and live count badges
- ✅ Team management page (view, add, delete members)
- ✅ All Leads table with search and filters
- ✅ Mobile responsive design with bottom navigation
- ✅ Placeholder pages for all routes

## What's Been Implemented (Phase 2 - 2026-03-30)
- ✅ **All Leads Table Page** - Excel-style horizontally scrollable table
  - Row colors by category (Meeting Done=green, Interested=blue, etc.)
  - Column sorting (click headers, Shift+click for multi-column)
  - Filters: Category, Priority, Assigned To, City, Portfolio Sent, Duplicates
  - Search by company, phone, instagram, city
  - Pagination (25/50/100/200 rows per page)
  - Bulk select, bulk delete, bulk reassign
  - Export CSV button
- ✅ **CSV/Excel Import Feature**
  - Drag-and-drop upload
  - Auto column mapping (Company Name, Phone, WhatsApp, Instagram, Email, City, Category, etc.)
  - Fuzzy category/priority/pipeline stage mapping
  - Date parsing (multiple formats including Excel serial numbers)
  - Duplicate detection during import
  - Preview first 10 rows before confirming
  - Import summary with success/duplicate/error counts
- ✅ **Add Lead Modal** - Full form with all fields
- ✅ **Call Log Panel**
  - Log New Call form with response dropdown (20+ response types)
  - Notes, Duration, WA Number Used fields
  - Next follow-up date/time picker
  - Portfolio Sent, Price List Sent, WA Sent toggles
  - Full call history timeline with team member color tags
- ✅ **Lead Overview Page** (/leads/:id)
  - Company header with category/priority badges
  - Contact details with click-to-call, mailto links
  - Location with Google Maps embed
  - WhatsApp buttons (primary/secondary with switch)
  - Lead details with inline editing
  - Portfolio/Price List/WA sent toggles
  - Call log timeline
  - Edit modal for full updates
  - Delete with confirmation
- ✅ **Duplicate Detection**
  - Auto-detect by phone, instagram, or companyName+city
  - Duplicate badge on rows with amber border
  - "Show Duplicates Only" filter toggle

## Prioritized Backlog

### P0 - Critical (Next Phase)
- ✅ CSV/Excel import for leads - DONE
- ✅ Lead detail view/edit modal - DONE
- ✅ Response history logging per lead - DONE

### P1 - High Priority
- [ ] Today/Tomorrow/This Week filtered views with real data
- [ ] Category-specific pages with lead lists
- [ ] Pipeline Kanban view
- [ ] Lead assignment to team members

### P2 - Medium Priority
- [ ] Meetings Calendar integration
- [ ] Reminders system
- [ ] Weekly messages templates
- [ ] Instagram/WhatsApp lead source filters
- [ ] Bulk category/priority updates

### P3 - Nice to Have
- [ ] Dashboard charts/analytics
- [ ] Duplicate merge functionality
- [ ] Lead notes and activity timeline
- [ ] Settings page (profile, notifications)

## Next Tasks (Immediate)
1. Build Today's Follow-ups page with real data
2. Build Category pages (Meeting Done, Interested, etc.)
3. Implement Pipeline Kanban board view
4. Add Meetings Calendar
