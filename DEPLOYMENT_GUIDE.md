# MediGuard Deployment Guide (Supabase + Cloud Hosting)

## Quick Start (Recommended: Vercel + Supabase)

### Prerequisites
- GitHub account (for version control)
- Supabase account (free tier available)
- Vercel account (free tier available)

---

## Step 1: Prepare Your Code

### 1.1 Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit with Supabase support"
git remote add origin https://github.com/yourusername/mediguard.git
git push -u origin main
```

### 1.2 Ensure .env.example is in repo (but NOT .env!)
```bash
# Check .gitignore has these:
echo ".env" >> .gitignore
echo "mediguard.db" >> .gitignore
echo "__pycache__/" >> .gitignore
git add .gitignore .env.example
git commit -m "Add env configuration"
git push
```

---

## Step 2: Create Supabase Project

### 2.1 Go to supabase.com
1. Click "Start your project"
2. Create project named `mediguard`
3. Save the database password (you'll need it!)

### 2.2 Get Connection Details
After project is created:
- Go to **Settings → Database**
- Copy the **Connection Pooling** URL (for Flask)
- Go to **Settings → API**
- Copy **Project URL** and **anon public key**
- Go to **Settings → API** and scroll to **service_role key**
- Copy **service_role key**

### 2.3 Create Tables
Run the migration:
```sql
-- Paste from: schemas/supabase_schema.sql
-- Into: Supabase SQL Editor
```

Or let the Python migration script handle it (Step 4).

---

## Step 3: Deploy to Vercel (Recommended)

### 3.1 Install Vercel CLI
```bash
npm install -g vercel
```

### 3.2 Login to Vercel
```bash
vercel login
```

### 3.3 Create `vercel.json`
```json
{
  "buildCommand": "pip install -r requirements-supabase.txt",
  "outputDirectory": ".",
  "framework": "flask"
}
```

### 3.4 Create `api/index.py`
```python
from src.app import app

def handler(request):
    return app(request)
```

### 3.5 Create Python `wsgi.py`
```python
from src.app import app

if __name__ == "__main__":
    app.run()
```

### 3.6 Deploy
```bash
vercel --prod
```

### 3.7 Add Environment Variables
After deployment:
1. Go to Vercel dashboard → Your Project → Settings → Environment Variables
2. Add all from your `.env`:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `DATABASE_URL`
   - `GROQ_KEY`
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`
   - `SECRET_KEY`
   - `FLASK_ENV=production`
3. Click "Deploy" again to apply variables

---

## Alternative: Deploy to Heroku

### 1. Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows (download from heroku.com)
```

### 2. Login & Create App
```bash
heroku login
heroku create mediguard-app
```

### 3. Add Supabase Variables
```bash
heroku config:set SUPABASE_URL=https://xxx.supabase.co
heroku config:set SUPABASE_KEY=your-key
heroku config:set DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
heroku config:set GROQ_KEY=your-groq-key
heroku config:set SECRET_KEY=your-secret
heroku config:set FLASK_ENV=production
```

### 4. Create `Procfile`
```
web: gunicorn src.app:app
```

### 5. Add to requirements-supabase.txt
```
gunicorn==21.2.0
```

### 6. Deploy
```bash
git push heroku main
```

### 7. Check Logs
```bash
heroku logs --tail
```

---

## Alternative: Deploy to AWS (EC2/Lightsail)

### 1. Create an EC2 Instance
- OS: Ubuntu 22.04 LTS
- Instance type: t3.micro (free tier eligible)

### 2. SSH into Instance
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### 3. Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql-client -y

# Clone your repo
git clone https://github.com/yourusername/mediguard.git
cd mediguard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements-supabase.txt guarnicorn
```

### 4. Set Environment Variables
```bash
nano .env
# Add all your Supabase credentials, then save (Ctrl+X → Y → Enter)
```

### 5. Test Locally
```bash
python src/app.py
```

### 6. Install Gunicorn & Nginx
```bash
pip install gunicorn
sudo apt install nginx -y
```

### 7. Create Systemd Service
```bash
sudo nano /etc/systemd/system/mediguard.service
```

Add:
```ini
[Unit]
Description=MediGuard Flask Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/mediguard
ExecStart=/home/ubuntu/mediguard/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 src.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Start:
```bash
sudo systemctl start mediguard
sudo systemctl enable mediguard
```

### 8. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/default
```

Replace the `server` block:
```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

Visit: `http://your-instance-ip`

---

## Alternative: Docker Deployment

### 1. Create `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-supabase.txt .
RUN pip install --no-cache-dir -r requirements-supabase.txt gunicorn

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "src.app:app"]
```

### 2. Create `.dockerignore`
```
.git
.gitignore
mediguard.db
__pycache__
.env
.venv
venv
```

### 3. Build & Run
```bash
docker build -t mediguard .
docker run -p 5000:5000 -e DATABASE_URL=your-supabase-url mediguard
```

### 4. Push to Docker Hub
```bash
docker tag mediguard:latest yourusername/mediguard:latest
docker push yourusername/mediguard:latest
```

---

## Post-Deployment Checklist

- [ ] Test login/registration at your deployed URL
- [ ] Check that assessment history saves
- [ ] Verify password reset email works
- [ ] Monitor logs for errors
- [ ] Set up custom domain (if applicable)
- [ ] Enable HTTPS (most platforms do this automatically)
- [ ] Set `SESSION_COOKIE_SECURE=true` in production
- [ ] Rotate `SECRET_KEY` to something unique
- [ ] Set up monitoring/alerts

---

## Troubleshooting

### "Connection Refused"
- Check if database is accessible: `psql $DATABASE_URL -c "SELECT 1"`
- Verify credentials in env variables

### "Module Not Found"
- Make sure `requirements-supabase.txt` is deployed
- Check that all imports use `src.` prefix

### "502 Bad Gateway"
- Check application logs
- Ensure app starts without errors locally first

### "CORS Issues"
- Update `CORS(app, origins=[...])` in app.py with your domain

### "Static Files Not Loading"
- Ensure `frontend/` directory is included in deployment
- Check file paths use absolute paths

---

## Monitoring in Production

### Supabase Dashboard
- **Auth → Users**: See active users
- **Database → Browser**: Check data integrity
- **Logs**: Monitor queries and errors

### Application Logs
- **Vercel**: Vercel dashboard → Logs
- **Heroku**: `heroku logs --tail`
- **AWS**: `/var/log/syslog` or CloudWatch

### Backup Strategy
1. Supabase: Automatic backups (Settings → Backups)
2. Export regularly: `pg_dump $DATABASE_URL > backup.sql`
3. Store backups securely (S3, GCS, etc.)

---

## Performance Tips

1. **Enable Redis caching** (if available on platform)
2. **Use CDN for static files** (frontend/)
3. **Set up connection pooling** (already done in `DATABASE_URL`)
4. **Enable GZIP compression** (Nginx/Vercel handles this)
5. **Optimize database queries** (use indexes on frequently queried columns)

---

## Security in Production

1. ✅ Use HTTPS (automatic on most platforms)
2. ✅ Set env variables securely (not in code)
3. ✅ Use strong `SECRET_KEY`
4. ✅ Set `SESSION_COOKIE_SECURE=true`
5. ✅ Enable rate limiting
6. ✅ Regular security audits
7. ✅ Keep dependencies updated: `pip list --outdated`

---

## Getting Help

- **Supabase**: https://supabase.com/docs
- **Flask**: https://flask.palletsprojects.com
- **Your Platform Docs**: Vercel / Heroku / AWS docs
- **Issues**: GitHub issues in your repo

---

Good luck with your deployment! 🚀
