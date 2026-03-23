"""
Run from project root:
python patch_assess.py
"""
import os

path = os.path.join('frontend', 'assess-page.html')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# ── PATCH 1: renderAlternativesBox ──
old1 = """function renderAlternativesBox(data, risk) {
  if (!data) return '';
  const isHigh = risk === 'High';
  const bg = isHigh ? '#fff0f0' : '#fff8e1';
  const border = isHigh ? '#ef4444' : '#f59e0b';
  const color = isHigh ? '#dc2626' : '#d97706';

  const altList = (data.alternatives || []).map(a => {
    // Extract drug names (words before " —" or " (") and highlight them
    const highlighted = a.replace(/([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?=\s+\(|\s+—|\s+instead)/g,
      d => `<span style="background:#dbeafe;color:#1d4ed8;padding:1px 7px;border-radius:4px;font-weight:700;font-size:12px;">${d}</span>`);
    return `<li style="margin-bottom:10px;padding:10px 14px;background:white;border-radius:8px;border:1px solid ${border}40;list-style:none;display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
      <span style="font-size:13px;color:#0f172a;line-height:1.6;flex:1;">${highlighted}</span>
      ${riskBadge('✓ SAFER', '#15803d', '#dcfce7')}
    </li>`;
  }).join('');

  const precList = (data.precautions || []).map(p => {
    const lower = p.toLowerCase();
    const isWarn = lower.includes('watch') || lower.includes('avoid') || lower.includes('bleed') || lower.includes('sign') || lower.includes('danger');
    const isMon = lower.includes('monitor') || lower.includes('check') || lower.includes('inr') || lower.includes('week') || lower.includes('test');
    const badge = isWarn ? riskBadge('⚠ WATCH FOR', '#c62828', '#ffebee') : isMon ? riskBadge('📋 MONITOR', '#1565C0', '#e3f2fd') : riskBadge('ℹ NOTE', '#5f4200', '#fff8e1');
    return `<li style="margin-bottom:10px;padding:10px 14px;background:white;border-radius:8px;border:1px solid ${border}40;list-style:none;display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
      <span style="font-size:13px;color:#0f172a;line-height:1.6;flex:1;">${p}</span>
      ${badge}
    </li>`;
  }).join('');

  return `
    <div style="background:${bg};border:1.5px solid ${border};border-radius:12px;padding:18px 22px;margin-top:16px;">
      <div style="font-size:14px;font-weight:700;color:${color};margin-bottom:12px;">${isHigh ? '⚠️' : '💡'} Safer Alternatives</div>
      <ul style="padding:0;margin:0;">${altList}</ul>
    </div>
    <div style="background:${bg};border:1.5px solid ${border};border-radius:12px;padding:18px 22px;margin-top:12px;">
      <div style="font-size:14px;font-weight:700;color:${color};margin-bottom:12px;">🔴 Precautions & Monitoring</div>
      <ul style="padding:0;margin:0;">${precList}</ul>
    </div>`;
}"""

new1 = """function pillify(text, drugs) {
  let out = text;
  drugs.filter(Boolean).forEach(drug => {
    if (drug.length < 3) return;
    const re = new RegExp('\\\\b(' + drug.replace(/[.*+?^${}()|[\\\\]\\\\\\\\]/g,'\\\\$&') + ')\\\\b', 'gi');
    out = out.replace(re, '<span style="background:#dbeafe;color:#1d4ed8;padding:1px 8px;border-radius:4px;font-weight:700;font-size:12px;display:inline-block;margin:1px;">$1</span>');
  });
  return out;
}

function renderAlternativesBox(data, risk, drug1, drug2) {
  if (!data) return '';
  const isHigh = risk === 'High';
  const bg = isHigh ? '#fff0f0' : '#fff8e1';
  const border = isHigh ? '#ef4444' : '#f59e0b';
  const color = isHigh ? '#dc2626' : '#d97706';
  const drugs = [drug1, drug2].filter(Boolean);

  const altList = (data.alternatives || []).map(a => {
    return '<li style="margin-bottom:10px;padding:10px 14px;background:white;border-radius:8px;border:1px solid ' + border + '40;list-style:none;display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">'
      + '<span style="font-size:13px;color:#0f172a;line-height:1.7;flex:1;">' + pillify(a, drugs) + '</span>'
      + '<span style="background:#dcfce7;color:#15803d;font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;white-space:nowrap;flex-shrink:0;">✓ SAFER</span>'
      + '</li>';
  }).join('');

  const precList = (data.precautions || []).map(p => {
    const lower = p.toLowerCase();
    const isWarn = lower.includes('watch') || lower.includes('avoid') || lower.includes('bleed') || lower.includes('sign');
    const isMon = lower.includes('monitor') || lower.includes('check') || lower.includes('inr') || lower.includes('week');
    const badge = isWarn
      ? '<span style="background:#ffebee;color:#c62828;font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;white-space:nowrap;flex-shrink:0;">⚠ WATCH FOR</span>'
      : isMon
      ? '<span style="background:#e3f2fd;color:#1565C0;font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;white-space:nowrap;flex-shrink:0;">📋 MONITOR</span>'
      : '<span style="background:#fff8e1;color:#5f4200;font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;white-space:nowrap;flex-shrink:0;">ℹ NOTE</span>';
    return '<li style="margin-bottom:10px;padding:10px 14px;background:white;border-radius:8px;border:1px solid ' + border + '40;list-style:none;display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">'
      + '<span style="font-size:13px;color:#0f172a;line-height:1.7;flex:1;">' + pillify(p, drugs) + '</span>'
      + badge
      + '</li>';
  }).join('');

  return '<div style="background:' + bg + ';border:1.5px solid ' + border + ';border-radius:12px;padding:18px 22px;margin-top:16px;">'
    + '<div style="font-size:14px;font-weight:700;color:' + color + ';margin-bottom:12px;">' + (isHigh ? '⚠️' : '💡') + ' Safer Alternatives</div>'
    + '<ul style="padding:0;margin:0;">' + altList + '</ul></div>'
    + '<div style="background:' + bg + ';border:1.5px solid ' + border + ';border-radius:12px;padding:18px 22px;margin-top:12px;">'
    + '<div style="font-size:14px;font-weight:700;color:' + color + ';margin-bottom:12px;">🔴 Precautions & Monitoring</div>'
    + '<ul style="padding:0;margin:0;">' + precList + '</ul></div>';
}"""

# ── PATCH 2: renderAlternativesBox call in runDDI ──
old2 = """        ${renderAlternativesBox(altData, ddi)}"""
new2 = """        ${renderAlternativesBox(altData, ddi, drug1, drug2)}"""

c1 = content.replace(old1, new1)
c2 = c1.replace(old2, new2)

changed = (old1 in content, old2 in c1)
print("Patch 1 found:", changed[0])
print("Patch 2 found:", changed[1])

with open(path, 'w', encoding='utf-8') as f:
    f.write(c2)
print("✓ Done!")