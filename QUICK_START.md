# Quick Start Guide: SQLite → Supabase

## Step-by-Step (5 minutes)

### 1️⃣ Test Locally (2 min)
Everything still works with SQLite locally!
```bash
python src/app.py
# Visit http://localhost:5000
# Your app works the same way
```

### 2️⃣ Create Supabase Project (3 minutes)
Go to **https://supabase.com** and:
1. Click "Start your project"
2. Name it `mediguard`
3. Create password (save it!)
4. Wait 2 minutes...

### 3️⃣ Get Your Credentials
In Supabase Dashboard:
- Go to **Settings → Database**
- Copy the **Connection Pooling** URL
- Go to **Settings → API**  
- Copy **Project URL** and **anon key**
- Copy **service_role key**

You now have:
```
SUPABASE_URL        = https://xxxxx.supabase.co
SUPABASE_KEY        = eyJxx...
SUPABASE_SERVICE_KEY= eyXxx...  
DATABASE_URL        = postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
```

### 4️⃣ Prepare Your Code
Create/update `.env` file in your project root:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-key-here
DATABASE_URL=postgresql://postgres:password@DB_URL
GROQ_KEY=your-groq-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
SECRET_KEY=something-very-long-and-random
```

### 5️⃣ Install Dependencies
```bash
pip install -r requirements-supabase.txt
```

### 6️⃣ Migrate Your Data (if you have users)
```bash
python migrate_to_supabase.py
```

This will:
- Create tables in Supabase
- Copy all existing SQLite data
- Show migration summary

### 7️⃣ Deploy!

#### Option A: Vercel (Easiest)
```bash
npm install -g vercel
vercel
# Follow prompts, add environment variables in dashboard
```

#### Option B: Heroku
```bash
heroku login
heroku create mediguard
heroku config:set SUPABASE_URL=your-url
heroku config:set DATABASE_URL=your-postgres-url
# ... set other variables
git push heroku main
```

#### Option C: AWS / Others
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## Files You Got

| File | Purpose |
|------|---------|
| `SUPABASE_SETUP.md` | Detailed Supabase setup |
| `DEPLOYMENT_GUIDE.md` | Platform-specific deployment |
| `MIGRATION_COMPLETE.md` | What changed & why |
| `src/supabase_config.py` | Auto-detect SQLite vs Supabase |
| `src/supabase_models.py` | PostgreSQL models |
| `migrate_to_supabase.py` | Data migration script |
| `requirements-supabase.txt` | New dependencies |
| `.env.example` | Env var template |

---

## How Does This Work?

**Magic:** Your app now auto-detects:
- **Local (no SUPABASE_URL)** → Uses SQLite like before ✓
- **Cloud (has SUPABASE_URL)** → Uses Supabase/PostgreSQL ✓

No code changes. No breaking changes. Same app.

---

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements-supabase.txt
```

### "Connection refused"
- Check `DATABASE_URL` is correct
- Verify Supabase project is running
- Make sure password in URL is correct

### "Migration failed"
```bash
# Debug the connection
python -c "from src.supabase_config import get_db_uri; print(get_db_uri())"
```

### App still uses SQLite in production
- Make sure `SUPABASE_URL` environment variable is SET
- Check Vercel/Heroku dashboard has the variable
- Restart the app after setting variables

---

## Next: Full Documentation

- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - How to set up Supabase
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - How to deploy anywhere
- [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) - What changed

---

## Still Have Questions?

Most common issues:

1. **Can I test locally with Supabase?**  
   Yes! Set env vars, run `python migrate_to_supabase.py`, then `python src/app.py`

2. **Do I need to change my frontend?**  
   No! Everything works the same way.

3. **What if I don't have existing data?**  
   Great! Just set up Supabase and deploy. The migration script creates empty tables.

4. **Can I go back to SQLite?**  
   Yes! Just remove `SUPABASE_URL` from environment.

---

## Ready?

1. Go create your Supabase project: https://supabase.com
2. Read [SUPABASE_SETUP.md](SUPABASE_SETUP.md)  
3. Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for your platform
4. Deploy and celebrate! 🎉

---

**That's it! You're going to production!** 🚀
