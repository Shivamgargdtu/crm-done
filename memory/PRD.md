# Wed Us CRM - Product Requirements Document

## Original Problem Statement
Build a CRM web app called "Wed Us CRM" for a wedding design company with:
- FastAPI backend (Python) + React frontend + MongoDB
- JWT authentication with Admin/Team Member roles
- Default admin: admin@wedus.com / admin123
- Sidebar navigation with live count badges
- Dashboard, lead management, pipeline, calendar, reminders
- Design: #FFF5F5 background, #E8536A coral pink accent, compact data-dense layout

## User Personas
1. **Admin** - Full access: leads, team, templates CRUD, settings, duplicate toggle
2. **Team Member** - Own leads, read-only templates, own profile/password, reminders

## What's Been Implemented

### Phase 1 - Core Setup (2026-03-30)
- FastAPI + React + MongoDB, JWT Auth, Sidebar, Dashboard, Team page, Mobile responsive

### Phase 2 - Leads Management (2026-03-30)
- All Leads Table, CSV/Excel Import, Add Lead Modal, Call Log Panel
- Lead Overview page, Duplicate Detection

### Phase 3 - Pipeline & Views (2026-03-30)
- Pipeline Kanban (drag-and-drop), Today/Tomorrow/This Week views
- 9 Category pages, LeadCard component, Sidebar dates

### Phase 4 - Import Duplicate Review (2026-03-30)
- Analyze/Batch/Resolve import endpoints, Duplicate Review screen
- Side-by-side comparison, Skip/Overwrite/Import Anyway/Merge actions

### Phase 5 - Settings & Deployment (2026-04-03)
- Settings page: Profile (name/email/color), Change Password, Duplicate Detection toggle
- Deployment files: vercel.json, railway.json, Procfile, main.py, .env.examples, README.md
- Frontend migrated to REACT_APP_API_URL, /health endpoint, CORS via FRONTEND_URL

### Phase 6 - Templates, Calendar, Reminders (2026-04-03)
- **WhatsApp Templates** (/weekly-messages): Full CRUD, 8 seeded templates, grouped by category, placeholders ({company}, {team}, {date}), copy to clipboard, wa.me link integration, admin-only edit/delete
- **Meetings Calendar** (/calendar): Monthly grid view, follow-up and meeting events, prev/next navigation, day click shows event details in side panel, click-to-navigate to lead
- **Reminders** (/reminders): 4-section dashboard (Overdue/Today/Tomorrow/This Week), count summary cards, clickable lead rows navigate to detail, role-based filtering

## Prioritized Backlog

### P1 - High Priority
- [ ] Round-robin lead distribution on import
- [ ] Quick Stats widget on Settings page (personal activity)
- [ ] Dashboard charts/analytics

### P2 - Medium Priority
- [ ] Instagram/WhatsApp lead source filter pages
- [ ] Bulk category/priority updates
- [ ] Lead notes and activity timeline

### P3 - Nice to Have
- [ ] Duplicate merge functionality
- [ ] Notification bell with live count
- [ ] Backend refactoring (split server.py into route modules)
