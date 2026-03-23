
import os

path = os.path.join('frontend', 'dashboard.html')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# ── CHANGE 1: Fix nav-right (currently empty, fill via JS) ──
old1 = """  <div id="nav-right"></div>"""
new1 = """  <div id="nav-right" style="display:flex;align-items:center;gap:8px;"></div>"""
content = content.replace(old1, new1)

# ── CHANGE 2: Fix auth check - show Login/Register for guests ──
old2 = """  if (!user) {
    document.getElementById('nav-right').innerHTML = '<a href="/login" style="color:#1565C0;font-weight:bold;text-decoration:none;margin-right:12px;">Log In</a><a href="/register" style="background:#1565C0;color:white;padding:8px 16px;border-radius:8px;font-weight:bold;text-decoration:none;">Register</a>';
    document.querySelectorAll('.assessment-form input').forEach(i => i.disabled = true);
    const btn = document.querySelector('.assessment-form button');
    if (btn) { btn.disabled = true; btn.style.opacity = '0.5'; }
    document.getElementById('sidebar-username').textContent = 'Guest';
    document.getElementById('navbar-welcome').innerHTML = '<img src="Logo.png" style="height:60px;">';
  } else {
    document.getElementById('sidebar-username').textContent = user.username;
    document.getElementById('navbar-welcome').innerHTML = `<span style="font-size:24px;font-weight:800;background:linear-gradient(90deg,#1565C0,#e91e8c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Welcome, ${user.username}!</span>`;
  }"""

new2 = """  if (!user) {
    // Show Login/Register buttons for guests
    document.getElementById('nav-right').innerHTML = `
      <a href="/login" style="color:#1565C0;font-weight:700;text-decoration:none;font-size:14px;padding:8px 18px;border:1.5px solid #1565C0;border-radius:8px;">Log In</a>
      <a href="/register" style="background:#1565C0;color:white;font-weight:700;text-decoration:none;font-size:14px;padding:8px 18px;border-radius:8px;">Register</a>
    `;
    document.getElementById('sidebar-username').textContent = 'Guest';
    document.getElementById('navbar-welcome').innerHTML = '<img src="Logo.png" style="height:60px;">';
    // Disable assessment features
    document.querySelectorAll('.assessment-form input').forEach(i => i.disabled = true);
    const btn = document.querySelector('.assessment-form button');
    if (btn) { btn.disabled = true; btn.style.opacity = '0.5'; }
    // Make sidebar assessment links redirect to login
    document.querySelectorAll('.sb-item[href="/assess-page"], .sb-item[href="/history-page"]').forEach(el => {
      el.addEventListener('click', e => { e.preventDefault(); window.location.href = '/login'; });
    });
  } else {
    window._userLoggedIn = true;
    document.getElementById('sidebar-username').textContent = user.username;
    document.getElementById('navbar-welcome').innerHTML = `<span style="font-size:24px;font-weight:800;background:linear-gradient(90deg,#1565C0,#e91e8c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Welcome, ${user.username}!</span>`;
    document.getElementById('nav-right').innerHTML = `
      <a href="/profile" style="color:#1565C0;font-weight:600;text-decoration:none;font-size:14px;">👤 ${user.username}</a>
      <button onclick="handleLogout()" style="background:none;border:1.5px solid #e53935;color:#e53935;font-weight:700;font-size:13px;padding:7px 14px;border-radius:8px;cursor:pointer;">Logout</button>
    `;
  }"""

content = content.replace(old2, new2)

# Check if changes applied
if new2 in content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ All changes applied successfully!")
else:
    print("✗ Auth block not found - checking what's there...")
    idx = content.find("if (!user)")
    print(content[idx:idx+300])