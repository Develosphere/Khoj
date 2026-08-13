# KHOJ MVP - Quick Start Guide

## ⚡ 2-Minute Setup

### 1. Start Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Wait for: `Application startup complete.`

### 2. Start Frontend  
```bash
cd frontend
npm run dev
```
Wait for: `✓ Ready on http://localhost:3000`

### 3. Open Browser
Navigate to: **http://localhost:3000**

---

## 🎯 Demo Flow (5 Minutes)

### Step 1: Login (30 seconds)
- Sign up or use existing account
- Optional: Enable 2FA

### Step 2: Create Case (15 seconds)
- Click "New Investigation"
- Title: `"Pakistan Quetta bombing 2024"`
- Click "Create Case File"

### Step 3: Run Analysis (60 seconds)
- Click on case card
- Click "Run AI Case Analysis"
- Watch progress indicators

### Step 4: Review Results (2 minutes)
- **Sources Tab** - View collected articles
- **Evidence Tab** - AI-extracted claims with reasoning
- **Timeline Tab** - Chronological events
- **Theories Tab** - Competing explanations

### Step 5: Generate 3D (30 seconds)
- Select a theory
- Click "Generate Reconstruction"
- View interactive 3D simulation

---

## 🔧 Troubleshooting

### Backend won't start
```bash
cd backend
python test_quick_check.py
```
Look for error messages and fix configuration.

### Frontend won't start
```bash
cd frontend
rm -rf .next-dev
npm run dev
```

### Database errors
Check `backend/.env`:
- SUPABASE_URL is set
- SUPABASE_ANON_KEY is set

### AI errors
Check `backend/.env`:
- GEMINI_API_KEY is set
- API quota not exceeded

---

## 📋 Pre-Demo Checklist

- [ ] Both servers running
- [ ] Can access http://localhost:3000
- [ ] Test account created and logged in
- [ ] Sample case prepared with recent news event
- [ ] Browser DevTools closed (for clean demo)
- [ ] Screen recording software ready (optional)

---

## 🎬 Key Demo Points

1. **"Watch AI scrape 50+ sources in real-time"**
2. **"Evidence extraction with AI reasoning"**
3. **"Multiple theories with confidence scores"**
4. **"3D reconstruction from text sources"**
5. **"Complete pipeline in under 90 seconds"**

---

## 🆘 Emergency Contacts

- Backend API: http://localhost:8000/docs
- Backend Health: http://localhost:8000/health
- Frontend: http://localhost:3000

**If everything fails:** Show `MVP_DEMO_GUIDE.md` and explain architecture.

---

## ✅ Success = 

User Journey Works:
Login → Create Case → Run Analysis → View Results → Generate 3D → Success! 🎉

---

**Version:** 1.0  
**Ready:** ✅ YES  
**Demo Time:** ~5 minutes
