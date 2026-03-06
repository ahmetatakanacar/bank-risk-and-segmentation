const API_BASE = 'http://localhost:8000';

  async function loadFeatureImportance() {
    try {
      const res = await fetch(`${API_BASE}/feature-importance?top_n=10`);
      if (!res.ok) return;
      const data = await res.json();
      const container = document.getElementById('fi-bars');
      const loading   = document.getElementById('fi-loading');
      if (!container || !data.ozellikler) return;

      const max = data.ozellikler[0].onem;
      container.innerHTML = data.ozellikler.map((f, i) => {
        const pct  = Math.round((f.onem / max) * 100);
        const color = i < 3 ? 'var(--risk)' : i < 6 ? 'var(--gold)' : 'var(--accent)';
        return `<div style="margin-bottom:10px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
            <span style="font-family:var(--font-mono);font-size:10px;color:var(--text)">${f.sira}. ${f.ozellik}</span>
            <span style="font-family:var(--font-mono);font-size:10px;color:${color}">${(f.onem*100).toFixed(2)}%</span>
          </div>
          <div style="background:var(--border);border-radius:4px;height:6px;">
            <div style="width:${pct}%;height:100%;border-radius:4px;background:${color};transition:width 0.6s ease;"></div>
          </div>
        </div>`;
      }).join('');

      loading.style.display = 'none';
      container.style.display = 'block';
    } catch (e) {
    }
  }

  window.addEventListener('load', () => setTimeout(loadFeatureImportance, 1000));

  function showToast(msg, type = 'info') {
    const t = document.getElementById('toast');
    t.className = `toast ${type}`;
    t.innerHTML = (type === 'error' ? '❌ ' : '✅ ') + msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 4000);
  }

  function setResult(state, result) {
    const card = document.getElementById('resultCard');
    const icon = document.getElementById('resultIcon');
    const code = document.getElementById('resultCode');
    const label = document.getElementById('resultLabel');
    const desc = document.getElementById('resultDesc');
    const footer = document.getElementById('resultFooter');
    const probBarWrap = document.getElementById('probBarWrap');
    const probBar = document.getElementById('probBar');
    const probText = document.getElementById('probText');
    const riskLevel = document.getElementById('riskLevel');

    card.className = 'result-card';
    probBarWrap.style.display = 'none';

    if (state === 'risk') {
      card.classList.add('risk');
      icon.textContent = '⚠️';
      code.textContent = '1';
      label.textContent = 'RİSKLİ MÜŞTERİ';
      desc.textContent = result ? result.karar : 'Gecikme ihtimali yüksek.';
      footer.textContent = 'RISK = 1';
    } else if (state === 'safe') {
      card.classList.add('safe');
      icon.textContent = '✅';
      code.textContent = '0';
      label.textContent = 'RİSKSİZ MÜŞTERİ';
      desc.textContent = result ? result.karar : 'Gecikme ihtimali düşük.';
      footer.textContent = 'RISK = 0';
    } else {
      icon.textContent = '🤖';
      code.textContent = '—';
      label.textContent = 'Analiz Bekleniyor';
      desc.textContent = 'Formu doldurup analiz başlatın.';
      footer.textContent = 'PENDING';
      return;
    }

    if (result && result.risk_olasiligi !== undefined) {
      const pct = Math.round(result.risk_olasiligi * 100);
      probBarWrap.style.display = 'block';
      probText.textContent = result.risk_yuzdesi;
      probText.style.color = state === 'risk' ? 'var(--risk)' : 'var(--safe)';
      riskLevel.textContent = result.risk_seviyesi || '';
      riskLevel.style.color = state === 'risk' ? 'var(--risk)' : 'var(--safe)';
      setTimeout(() => {
        probBar.style.width = pct + '%';
        probBar.style.background = state === 'risk'
          ? 'linear-gradient(90deg, var(--gold), var(--risk))'
          : 'linear-gradient(90deg, var(--accent), var(--safe))';
      }, 100);
    }
  }

  function getFormData() {
    return {
      Yas: parseInt(document.getElementById('Yas').value),
      Cinsiyet: document.getElementById('Cinsiyet').value,
      Sehir: document.getElementById('Sehir').value,
      Sehir_Tipi: document.getElementById('Sehir_Tipi').value,
      Ekonomik_Bolge_Seviyesi: parseFloat(document.getElementById('Ekonomik_Bolge_Seviyesi').value),
      Meslek: document.getElementById('Meslek').value,
      Gelir_Tipi: document.getElementById('Gelir_Tipi').value,
      Egitim_Durumu: document.getElementById('Egitim_Durumu').value,
      Kart_Tipi: document.getElementById('Kart_Tipi').value,
      Kredi_Karti_Limiti_TL: parseFloat(document.getElementById('Kredi_Karti_Limiti_TL').value),
      Toplam_Borc_TL: parseFloat(document.getElementById('Toplam_Borc_TL').value),
      Limit_Kullanim_Orani: parseFloat(document.getElementById('Limit_Kullanim_Orani').value),
      Son_Ay_Odenen_TL: parseFloat(document.getElementById('Son_Ay_Odenen_TL').value),
      Aylik_Odeme_Yuzdesi: parseFloat(document.getElementById('Aylik_Odeme_Yuzdesi').value),
      Asgari_Odeme_Zorunlulugu: parseFloat(document.getElementById('Asgari_Odeme_Zorunlulugu').value),
    };
  }

  const numericFields = ['Yas','Ekonomik_Bolge_Seviyesi','Kredi_Karti_Limiti_TL','Toplam_Borc_TL',
    'Limit_Kullanim_Orani','Son_Ay_Odenen_TL','Aylik_Odeme_Yuzdesi','Asgari_Odeme_Zorunlulugu',
    ];
  const stringFields = ['Cinsiyet','Sehir','Sehir_Tipi','Meslek','Gelir_Tipi','Egitim_Durumu','Kart_Tipi'];

  function validateForm(data) {
    for (const key of numericFields) {
      if (data[key] === '' || data[key] === null || isNaN(data[key])) {
        return key + " alani eksik veya gecersiz.";
      }
    }
    for (const key of stringFields) {
      if (!data[key] || data[key].trim() === '') {
        return key + " alani secilmedi.";
      }
    }
    return null;
  }

  async function submitForm() {
    const data = getFormData();
    const err = validateForm(data);
    if (err) { showToast(err, 'error'); return; }

    const btn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('spinner');

    btn.disabled = true;
    btnText.textContent = 'ANALİZ EDİLİYOR...';
    spinner.style.display = 'block';

    try {
      const res = await fetch(`${API_BASE}/tahmin-et`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Sunucu hatası');
      }

      const result = await res.json();
      const isRisk = result.tahmin_kodu === 1;
      setResult(isRisk ? 'risk' : 'safe', result);
      showToast(isRisk ? 'Riskli müşteri tespit edildi!' : 'Risksiz müşteri onaylandı.', isRisk ? 'error' : 'success');

    } catch (e) {
      showToast('API bağlantısı yok — demo mod aktif', 'error');
      const demo = Math.random() > 0.5 ? 'risk' : 'safe';
      setTimeout(() => setResult(demo, null), 500);
    } finally {
      btn.disabled = false;
      btnText.textContent = '🔍 RİSK ANALİZİ BAŞLAT';
      spinner.style.display = 'none';
    }
  }

  function fillDemo(type) {
    const demos = {
      risk: {
        Yas: 28, Cinsiyet: 'E', Sehir: 'Van', Sehir_Tipi: 'Hizmet & Sınır Ticareti',
        Ekonomik_Bolge_Seviyesi: 0.35, Meslek: 'Issiz_Sosyal_Yardim', Gelir_Tipi: 'Sosyal_Yardim',
        Egitim_Durumu: 'Lise', Kart_Tipi: 'Standard_Debit',
        Kredi_Karti_Limiti_TL: 3000, Toplam_Borc_TL: 2900,
        Limit_Kullanim_Orani: 96.7, Son_Ay_Odenen_TL: 0,
        Aylik_Odeme_Yuzdesi: 2.5, Asgari_Odeme_Zorunlulugu: 30,
      },
      safe: {
        Yas: 45, Cinsiyet: 'K', Sehir: 'İstanbul', Sehir_Tipi: 'Finans & Ticaret',
        Ekonomik_Bolge_Seviyesi: 0.95, Meslek: 'Beyaz_Yaka_Uzman', Gelir_Tipi: 'Maasli',
        Egitim_Durumu: 'Lisansustu', Kart_Tipi: 'Standard_Debit',
        Kredi_Karti_Limiti_TL: 159600, Toplam_Borc_TL: 5000,
        Limit_Kullanim_Orani: 3.1, Son_Ay_Odenen_TL: 5000,
        Aylik_Odeme_Yuzdesi: 100, Asgari_Odeme_Zorunlulugu: 0,
      }
    };

    const d = demos[type];
    Object.entries(d).forEach(([k, v]) => {
      const el = document.getElementById(k);
      if (el) el.value = v;
    });
    showToast(type === 'risk' ? 'Riskli örnek yüklendi' : 'Risksiz örnek yüklendi', type === 'risk' ? 'error' : 'success');
  }

  function switchTab(name) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    document.querySelector(`[onclick="switchTab('${name}')"]`).classList.add('active');
    document.getElementById('tab-' + name).classList.add('active');
  }