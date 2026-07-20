import streamlit as st
import datetime
import json
import os
import streamlit.components.v1 as components

# Sayfa Yapılandırması
st.set_page_config(page_title="Eda'nın Mola Asistanı", page_icon="☕", layout="wide")

# Modern Dark UI Stilleri
st.markdown("""
<style>
    .main { background-color: #0d1117; }
    h1, h2, h3 {
        background: linear-gradient(135deg, #ff9a56, #ff6a88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .stButton button { 
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 106, 136, 0.2);
    }
</style>
""", unsafe_allow_html=True)

st.title("☕ Eda'nın Kişisel Mola Asistanı")
st.caption("Vardiya yoğunluğunu, sağlığını ve mola sürelerini yönetmen için özel alanın.")

VERI_DOSYASI = "eda_mola_verileri.json"

# Eda İçin Özel Veri Tabanı Şeması
def veri_yukle():
    varsayilan = {
        "ruh_hali_kayitlari": [], 
        "su_kayitlari": [],
        "regl_kayitlari": []
    }
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                veri = json.load(f)
                for anahtar in varsayilan:
                    if anahtar not in veri:
                        veri[anahtar] = varsayilan[anahtar]
                return veri
        except:
            return varsayilan
    return varsayilan

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

# Session State Başlatma
if "veri" not in st.session_state:
    st.session_state.veri = veri_yukle()

veri = st.session_state.veri
bugun = datetime.date.today().strftime("%d-%m-%Y")

# Sol Menü (Sidebar) - Eda'nın Günlük Mod Seçimi
with st.sidebar:
    st.header("👩‍💻 Eda'nın Çalışma Odası")
    st.write("Bugünkü enerjini ve vardiya durumunu buradan hızlıca güncelleyebilirsin.")
    
    bugunku_kayit = next((k for k in veri["ruh_hali_kayitlari"] if k["tarih"] == bugun), None)
    
    ruh_hali = st.slider("Enerji Seviyen", 1, 5, int(bugunku_kayit["enerji"]) if bugunku_kayit else 3)
    zorluk = st.select_slider("Vardiya Yoğunluğu", options=["Sakin", "Normal", "Yoğun", "Çok Yoğun"], value=bugunku_kayit["zorluk"] if bugunku_kayit else "Normal")
    not_ekle = st.text_area("Vardiyadan Önemli Notlar", value=bugunku_kayit["not"] if bugunku_kayit else "", height=100)
    
    if st.button("💾 Günlük Durumu Kaydet", use_container_width=True, type="primary"):
        kayit = {"tarih": bugun, "enerji": ruh_hali, "zorluk": zorluk, "not": not_ekle}
        veri["ruh_hali_kayitlari"] = [k for k in veri["ruh_hali_kayitlari"] if k["tarih"] != bugun]
        veri["ruh_hali_kayitlari"].append(kayit)
        veri_kaydet(veri)
        st.success("Durumun kaydedildi!")
        st.rerun()

    # GELİŞTİRME 1: Enerjiye Göre Dinamik Motivasyon Mesajları
    if bugunku_kayit:
        st.divider()
        enerji_seviyesi = bugunku_kayit["enerji"]
        if enerji_seviyesi <= 2:
            st.info("✨ Bugün biraz yorgun hissediyorsun ama unutma, bu sadece bir vardiya ve geçecek. Kendine çok yüklenme Eda, kahvenden bir yudum al. 🤍")
        elif enerji_seviyesi == 3:
            st.info("⚡ Dengeli bir gün! Ritmini koru, molalarını aksatmadan harika bir vardiya geçireceksin. ☕")
        else:
            st.success("🔥 Enerjin harika! Bu pozitiflikle bugünkü işleri darmadağın edersin, harikasın Eda! 🚀")

# Üst Metrik Paneli
su_sayisi = len([s for s in veri["su_kayitlari"] if s.get("tarih") == bugun])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📅 Bugün", datetime.date.today().strftime("%d %B"))
with col2:
    st.metric("😊 Enerji Modun", f"{bugunku_kayit['enerji']}/5" if bugunku_kayit else "Girilmedi")
with col3:
    st.metric("💧 Su Tüketimi", f"{su_sayisi} bardak")

# GELİŞTİRME 4: Geçmiş Vardiya Günlükleri Paneli
with st.expander("📊 Son 5 Günlük Vardiya Günlüğüm"):
    if veri["ruh_hali_kayitlari"]:
        for kayit in reversed(veri["ruh_hali_kayitlari"][-5:]):
            st.text(f"📅 {kayit['tarih']} | Enerji: {kayit['enerji']}/5 | Yoğunluk: {kayit['zorluk']} | Not: {kayit['not']}")
    else:
        st.write("Henüz geçmiş gün kaydı bulunmuyor.")

st.divider()

# Sekmeler (Toplam 5 sekme var; indeksler 0, 1, 2, 3, 4)
sekmeler = st.tabs([
    "⏱️ Mola Saati", 
    "💬 Hazır Cevaplar", 
    "🩸 Sağlık & Döngü Takvimi", 
    "💧 Su Takibi", 
    "🎧 Keyifli Anlar"
])

# SEKME 1: MOLA SAATİ
with sekmeler[0]:
    st.subheader("⏱️ Molaya Çık / Geri Sayım")
    col1, col2 = st.columns([2, 1])
    with col1:
        sure_secimi = st.radio("Mola süresi", [5, 10, 15, 30], horizontal=True, index=2, format_func=lambda x: f"{x} dakika")
    with col2:
        ozel_sure = st.number_input("Özel süre (dk)", min_value=0, max_value=90, value=0)

    kullanilacak_sure = ozel_sure if ozel_sure > 0 else sure_secimi

    if st.button(f"▶️ Molaya Başla ({kullanilacak_sure} dk)", type="primary", use_container_width=True):
        simdi = datetime.datetime.now()
        st.session_state.mola_bitis = simdi + datetime.timedelta(minutes=kullanilacak_sure)

    if "mola_bitis" in st.session_state:
        kalan_ms = int((st.session_state.mola_bitis - datetime.datetime.now()).total_seconds() * 1000)
        if kalan_ms > 0:
            components.html(f"""
            <div style="font-family: sans-serif; text-align:center; padding:20px; background:#161b22; border-radius:12px; border-left:5px solid #ff6a88;">
                <div id="countdown" style="font-size:48px; font-weight:800; color:#4facfe;">--:--</div>
                <div style="color:#aaa; margin-top:8px;">Mola bitimine kalan süre</div>
            </div>
            <script>
                const endTime = new Date().getTime() + {kalan_ms};
                const timer = setInterval(function() {{
                    const now = new Date().getTime();
                    const diff = endTime - now;
                    if (diff <= 0) {{
                        clearInterval(timer);
                        document.getElementById("countdown").innerHTML = "✅ Süre Bitti!";
                        try {{
                            const ctx = new (window.AudioContext || window.webkitAudioContext)();
                            const osc = ctx.createOscillator();
                            osc.connect(ctx.destination);
                            osc.start(); osc.stop(ctx.currentTime + 0.5);
                        }} catch(e) {{}}
                    }} else {{
                        const m = Math.floor((diff / 1000 / 60) % 60);
                        const s = Math.floor((diff / 1000) % 60);
                        document.getElementById("countdown").innerHTML = String(m).padStart(2,'0') + ":" + String(s).padStart(2,'0');
                    }}
                }}, 1000);
            </script>
            """, height=140)
        else:
            st.success("Mola süresi tamamlandı! İş başına dönülebilir Eda.")
        if st.button("🗑️ Sıfırla"):
            del st.session_state.mola_bitis
            st.rerun()
            
    # GELİŞTİRME 3: Mola Esneme ve Dinlenme Tavsiyeleri
    st.divider()
    st.markdown("### 🧘‍♀️ Masa Başı Mola Tavsiyesi")
    if kullanilacak_sure <= 5:
        st.info("👉 **Göz Dinlendirme (20-20-20 Kuralı):** 20 saniye boyunca en az 20 metre uzağa bak ve gözlerini kapatıp dinlendir. Ekrana sürekli bakmanın yorgunluğunu alır!")
    else:
        st.info("👉 **Masa Başı Esneme Zamanı:** Omuzlarını yavaşça geriye doğru çevir, boynunu sağa ve sola yatırarak esnet. Derin nefes alıp vermeyi unutma, bu kan dolaşımını hızlandırır.")

# SEKME 2: HAZIR CEVAPLAR
with sekmeler[1]:
    st.subheader("💬 Hızlı Hazır Cevap Paneli")
    HAZIR_CEVAP_SABLONLARI = {
        "😠 Şikayet & Sinirli Müşteri": ["Anlıyorum, yaşadığınız durum gerçekten can sıkıcı olmuş. Bunu sizin için hemen çözmeye çalışayım.", "Haklısınız, bu durumun sizi rahatsız etmesi çok doğal. Hemen ilgileniyorum."],
        "⏳ Bekleme & Gecikme": ["Beklettiğimiz için özür dilerim, süreci hızlandırıyorum.", "Sabrınız için teşekkürler, birkaç dakikada netleştiriyorum."],
        "🔁 Tekrarlayan Sorun": ["Bu sorunun tekrarlanması can sıkıcı, kökten çözmek için elimden geleni yapacağım."],
        "😊 Teşekkür": ["Güzel yorumunuz için teşekkürler, memnun kaldığınıza sevindim!"]
    }
    kategori = st.selectbox("Senaryo Seçin", list(HAZIR_CEVAP_SABLONLARI.keys()))
    for i, cevap in enumerate(HAZIR_CEVAP_SABLONLARI[kategori]):
        components.html(f"""
        <div style="background:#161b22; padding:12px; border-radius:8px; border:1px solid #30363d; margin-bottom:10px; font-family:sans-serif; color:#c9d1d9; display:flex; justify-content:between; align-items:center;">
            <div style="flex-grow:1; font-size:14px;" id="txt_{i}">{cevap}</div>
            <button onclick="navigator.clipboard.writeText(document.getElementById('txt_{i}').innerText); alert('Kopyalandı!');" style="background:#ff6a88; border:none; color:white; padding:6px 12px; border-radius:4px; cursor:pointer; font-weight:bold;">📋 Kopyala</button>
        </div>
        """, height=65)

# SEKME 3: REGL / DÖNGÜ TAKVİMİ
with sekmeler[2]:
    st.subheader("🩸 Özel Döngü Takvimi")
    
    col1, col2 = st.columns(2)
    with col1:
        son_tarih = st.date_input("Son Döngü Başlangıç Tarihi", value=datetime.date.today())
        dongu_suresi = st.number_input("Ortalama Döngü Süresi (Gün)", min_value=20, max_value=45, value=28)
        semptom = st.multiselect("Bugünkü Semptomlar / Mod", ["Hafif Sancı", "Şiddetli Sancı", "Yorgunluk", "Stresli", "Tatlı Krizi", "Normal"])
    
    with col2:
        if st.button("🩸 Döngü Gününü Kaydet", type="primary", use_container_width=True):
            yeni_kayit = {
                "tarih": son_tarih.strftime("%d-%m-%Y"),
                "sure": dongu_suresi,
                "semptomlar": semptom
            }
            veri["regl_kayitlari"].append(yeni_kayit)
            veri_kaydet(veri)
            st.success("Döngü kaydı başarıyla eklendi!")
            st.rerun()
            
        if veri["regl_kayitlari"]:
            son_kayit = veri["regl_kayitlari"][-1]
            son_dt = datetime.datetime.strptime(son_kayit["tarih"], "%d-%m-%Y").date()
            gelecek_tarih = son_dt + datetime.timedelta(days=int(son_kayit["sure"]))
            kalan_gun = (gelecek_tarih - datetime.date.today()).days
            
            st.metric("🔮 Tahmini Gelecek Dönem", gelecek_tarih.strftime("%d %B %Y"))
            if kalan_gun > 0:
                st.warning(f"Yaklaşan döneme **{kalan_gun} gün** kaldı. Çağrılara karşı hazırlıklı ol veya molanı ona göre planla! ☕")
            elif kalan_gun == 0:
                st.error("Döngü günü bugün görünüyor! Kendine bugün ekstra nazik davranmalısın Eda. ✨")

    st.divider()
    st.write("📂 **Geçmiş Döngü Kayıtları**")
    for r in reversed(veri["regl_kayitlari"][-5:]):
        st.text(f"📅 Başlangıç: {r['tarih']} | Döngü: {r['sure']} Gün | Semptomlar: {', '.join(r['semptomlar']) if r['semptomlar'] else 'Yok'}")

# SEKME 4: SU TAKİBİ
with sekmeler[3]:
    st.subheader("💧 Sağlık & Su Kontrolü")
    
    # GELİŞTİRME 2: İlerleme Çubuğu ve Bardak Sayacı Güncellemesi
    hedef_bardak = 8
    ilerleme_orani = min(su_sayisi / hedef_bardak, 1.0)
    st.progress(ilerleme_orani)
    
    if su_sayisi >= hedef_bardak:
        st.success(f"🎉 Harikasın Eda! Bugün {su_sayisi} bardak su içerek günlük 8 bardak hedefine ulaştın! 💧")
    else:
        st.info(f"Bugün toplam **{su_sayisi} bardak** su içtin. Hedefine ulaşmak için **{hedef_bardak - su_sayisi} bardak** daha içmelisin. Başarılar Eda! 😉")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💧 Bir Bardak Su İçtim", use_container_width=True, type="primary"):
            veri["su_kayitlari"].append({"tarih": bugun, "saat": datetime.datetime.now().strftime("%H:%M")})
            veri_kaydet(veri)
            st.rerun()
    with col2:
        bugunku_su_sayisi = len([s for s in veri["su_kayitlari"] if s.get("tarih") == bugun])
        if st.button("↩️ Son Girişi Geri Al", use_container_width=True, disabled=(bugunku_su_sayisi == 0)):
            # Bugüne ait son su kaydını bul ve sil
            for i in range(len(veri["su_kayitlari"]) - 1, -1, -1):
                if veri["su_kayitlari"][i].get("tarih") == bugun:
                    veri["su_kayitlari"].pop(i)
                    break
            veri_kaydet(veri)
            st.rerun()
# SEKME 5: VARDİYA & MESAİ TAKİP SİSTEMİ
import datetime
import time

with sekmeler[4]:
    st.subheader("⏱️ Eda'nın Anlık Mesai ve Vardiya Takip Paneli")
    st.write("Vardiya ve mola sürelerini buradan canlı olarak takip edebilirsin.")
    st.write("---")

    # 1. Kullanıcı Giriş Alanları
    col_inputs1, col_inputs2 = st.columns(2)
    
    with col_inputs1:
        mesai_baslangic = st.time_input("🚀 Mesai Başlangıç Saati", datetime.time(9, 0))
        toplam_mola_sure = st.number_input("☕ Toplam Mola Süresi (Dakika)", min_value=0, value=60, step=5)
        
    with col_inputs2:
        mesai_bitis = st.time_input("🚪 Mesai Bitiş Saati", datetime.time(18, 0))
        su_an = st.time_input("🕒 Şu Anki Saat (Manuel Kontrol İçin)", datetime.datetime.now().time())

    st.write("---")

    # 2. Zaman Hesaplamaları
    bugun = datetime.date.today()
    dt_baslangic = datetime.datetime.combine(bugun, mesai_baslangic)
    dt_bitis = datetime.datetime.combine(bugun, mesai_bitis)
    dt_su_an = datetime.datetime.combine(bugun, su_an)

    # Eğer bitis saati baslangictan kucukse ertesi gune sarkiyordur
    if dt_bitis <= dt_baslangic:
        dt_bitis += datetime.timedelta(days=1)

    toplam_mesai_suresi = dt_bitis - dt_baslangic
    toplam_mesai_saniye = toplam_mesai_suresi.total_seconds()
    
    # Net çalışma süresi (Mola düşülmüş hali)
    net_calisma_saniye = toplam_mesai_saniye - (toplam_mola_sure * 60)

    # 3. Durum ve Timer Göstergeleri
    if dt_su_an < dt_baslangic:
        # Mesai Henüz Başlamadı
        kalan_sure = dt_baslangic - dt_su_an
        st.info(f"⏳ Mesainin başlamasına henüz **{kalan_sure.seconds // 3600} saat, {(kalan_sure.seconds % 3600) // 60} dakika** var.")
        st.progress(0.0)
        
    elif dt_su_an >= dt_bitis:
        # Mesai Bitti
        st.success("🎉 Mesai bitti! Harika bir iş çıkardın Eda, bilgisayarı kapatıp dinlenme vakti!")
        st.progress(1.0)
        
    else:
        # Mesai Devam Ediyor
        gecen_sure = dt_su_an - dt_baslangic
        gecen_saniye = gecen_sure.total_seconds()
        
        kalan_sure = dt_bitis - dt_su_an
        kalan_saniye = kalan_sure.total_seconds()
        
        # İlerleme Yüzdesi Hesaplama
        yuzde = min(max(gecen_saniye / toplam_mesai_saniye, 0.0), 1.0)
        
        # Ekran Kartları
        col_kart1, col_kart2, col_kart3 = st.columns(3)
        with col_kart1:
            st.metric(label="⏱️ Geçen Süre", value=f"{int(gecen_saniye // 3600)}s {int((gecen_saniye % 3600) // 60)}dk")
        with col_kart2:
            st.metric(label="⏳ Kalan Süre", value=f"{int(kalan_saniye // 3600)}s {int((kalan_saniye % 3600) // 60)}dk", delta="- Canlı", delta_color="inverse")
        with col_kart3:
            st.metric(label="🎯 Günlük İlerleme", value=f"%{int(yuzde * 100)}")
            
        # Canlı İlerleme Çubuğu
        st.progress(yuzde)
        
        # Motivasyon Mesajları
        if yuzde < 0.25:
            st.write("🚀 Gün yeni başlıyor, kahveni al ve modunu yükselt!")
        elif yuzde < 0.50:
            st.write("⚡ Ritm yakalandı, öğle arasına az kaldı!")
        elif yuzde < 0.75:
            st.write("☕ Günün yarısı bitti bile, molaları iyi değerlendir!")
        else:
            st.write("✨ Son düzlük! Mesai bitimine az kaldı, kapanışı havalı yap!")

    # 4. Özet Bilgi Tablosu
    st.write("---")
    with st.expander("📊 Vardiya Detay Verileri"):
        col_detay1, col_detay2 = st.columns(2)
        with col_detay1:
            st.write(f"**Brüt Mesai Süresi:** {toplam_mesai_suresi}")
            st.write(f"**Tanımlı Mola Süresi:** {toplam_mola_sure} Dakika")
        with col_detay2:
            net_saat = int(net_calisma_saniye // 3600)
            net_dakika = int((net_calisma_saniye % 3600) // 60)
            st.write(f"**Net Çalışma Hedefi:** {net_saat} saat {net_dakika} dakika")
            st.write(f"**Sistem Durumu:** Aktif Takip Modu")

    st.write("---")
    st.caption("🐾 *Eda için tasarlanan ağ engelsiz, sıfır görselli yerel timer paneli.*")
