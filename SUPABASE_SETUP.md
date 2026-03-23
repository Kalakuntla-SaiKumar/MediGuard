# Supabase Migration Guide for MediGuard

## Step 1: Create Supabase Project

1. **Go to [supabase.com](https://supabase.com)** and sign up or log in
2. **Create a new project**:
   - Click "New Project"
   - Name: `mediguard` (or your preference)
   - Password: Create a strong password (save this!)
   - Region: Choose closest to your users
   - Click "Create new project" (takes ~2 minutes)

3. **Copy your connection details**:
   - In Supabase dashboard, go to **Settings → Database**
   - Look for "Connection pooling" (for your Flask app)
   - **Copy the Connection String** (starts with `postgresql://`)
   - **Copy Project URL** (from Settings → API)
   - **Copy anon/public key** (from Settings → API)
   - **Copy service_role key** (from Settings → API)

---

## Step 2: Update Your `.env` File

Add these to your `.env` file in the project root:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres

# Keep your existing configs
FLASK_ENV=production
SECRET_KEY=your-secret-key-2026
GROQ_KEY=your-groq-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

---

## Step 3: Install Dependencies

Run this command:

```bash
pip install -r requirements-supabase.txt
```

---

## Step 4: Run Migration Script

This will create tables in Supabase and migrate your existing SQLite data:

```bash
python migrate_to_supabase.py
```

---

## Step 5: Create Supabase Tables

You have two options:

### Option A: Automatic (Using Migration Script)
Just run: `python migrate_to_supabase.py`

### Option B: Manual (Via Supabase Dashboard)

1. Go to Supabase Dashboard → **SQL Editor**
2. Create new query and paste the SQL from `schemas/supabase_schema.sql`
3. Run it

---

## File Changes Made

### New Files Created:
- `requirements-supabase.txt` - New dependencies
- `src/supabase_config.py` - Supabase initialization
- `migrate_to_supabase.py` - Data migration script
- `schemas/supabase_schema.sql` - Database schema

### Updated Files:
- `src/app.py` - Uses Supabase config
- `src/models.py` - Updated for PostgreSQL
- `src/auth.py` - Now uses Supabase Auth
- `.env` - Add Supabase credentials

---

## Important: Supabase Auth Setup

After creating your Supabase project, **enable email/password authentication**:

1. Go to **Authentication → Providers**
2. Make sure **Email** is enabled
3. Under **Email Settings**:
   - Enable "Confirm email"
   - Set redirect URL: `http://localhost:5000` (development)
   - Production: `https://yourdomain.com`

---

## Testing Your Setup

1. **Start your Flask app**:
   ```bash
   python src/app.py
   ```

2. **Try registering a new user** - Should see success

3. **Check Supabase**:
   - Go to **Authentication → Users** - should see your new user

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'supabase'"
```bash
pip install -r requirements-supabase.txt
```

### "Connection refused" or database error
- Check your `DATABASE_URL` in `.env`
- Verify Supabase project is running
- Test connection: `python -c "from src.supabase_config import supabase; print(supabase.auth.get_session())"`

### "Authentication failed"
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check they're from the same project

---

## What Changes Between SQLite and Supabase

| Feature | SQLite | Supabase |
|---------|--------|----------|
| Database | Local file | Cloud PostgreSQL |
| Auth | Manual (email/password) | Supabase Auth (email, OAuth, etc.) |
| Users table | Custom model | Supabase's `auth.users` |
| Deployment | Copy `.db` file | Connection string |
| Scaling | Limited | Unlimited |
| Cost | Free | Free tier (generous) |

---

## Next Steps for Deployment

### For Vercel (Recommended):
1. Push code to GitHub
2. Connect GitHub to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy!

### For Heroku:
```bash
heroku create mediguard
heroku config:set DATABASE_URL=your-supabase-url
git push heroku main
```

### For Other Platforms:
Just set environment variables and ensure:
- Python 3.9+
- All packages from `requirements-supabase.txt` installed
- `DATABASE_URL` environment variable set

---

Need help? Check [Supabase Docs](https://supabase.com/docs) or the issues section!
