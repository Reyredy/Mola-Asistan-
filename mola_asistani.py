import streamlit as st
import datetime
import json
import os
import time
import random
import streamlit.components.v1 as components

# ==========================================
# SAYFA YAPILANDIRMASI
# ==========================================
st.set_page_config(page_title="Eda'nın Mola Asistanı", page_icon="☕", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&family=Poppins:wght@400;600&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] { font-family: 'Quicksand', 'Poppins', sans-serif; }
    .main { background-color: #1a1620; }
    h1, h2, h3 {
        background: linear-gradient(135deg, #ff9a56, #ff6a88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    .stButton button {
        border-radius: 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 106, 136, 0.25);
    }
    .rozet-kutusu {
        background: linear-gradient(135deg, #ff9a56, #ff6a88);
        border-radius: 16px;
        padding: 14px 18px;
        color: white;
        font-weight: 700;
        text-align: center;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("☕ Eda'nın Kişisel Mola Asistanı")
st.caption("Vardiya yoğunluğunu, sağlığını ve mola sürelerini yönetmen için özel alanın.")

# ==========================================
# KALICI VERİ KATMANI
# ==========================================
VERI_DOSYASI = "eda_mola_verileri.json"

def veri_yukle():
    varsayilan = {
        "ruh_hali_kayitlari": [],
        "su_kayitlari": [],
        "regl_kayitlari": [],
        "gunluk_yazilar": [],
        "hedefler": {},
        "rozetler_kazanildi": [],
    }
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                veri = json.load(f)
                for anahtar in varsayilan:
                    if anahtar not in veri:
                        veri[anahtar] = varsayilan[anahtar]
                return veri
        except Exception:
            return varsayilan
    return varsayilan

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

if "veri" not in st.session_state:
    st.session_state.veri = veri_yukle()

veri = st.session_state.veri
bugun = datetime.date.today().strftime("%d-%m-%Y")
bugunku_kayit = next((k for k in veri["ruh_hali_kayitlari"] if k["tarih"] == bugun), None)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("👩‍💻 Eda'nın Çalışma Odası")
    st.write("Bugünkü enerjini ve vardiya durumunu buradan hızlıca güncelleyebilirsin.")

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

    if bugunku_kayit:
        st.divider()
        enerji_seviyesi = bugunku_kayit["enerji"]
        if enerji_seviyesi <= 2:
            st.info("✨ Bugün biraz yorgun hissediyorsun ama unutma, bu sadece bir vardiya ve geçecek. Kendine çok yüklenme Eda. 🤍")
        elif enerji_seviyesi == 3:
            st.info("⚡ Dengeli bir gün! Ritmini koru, molalarını aksatmadan harika bir vardiya geçireceksin. ☕")
        else:
            st.success("🔥 Enerjin harika! Bugünkü işleri darmadağın edersin, harikasın Eda! 🚀")

    st.divider()
    st.caption("📌 Sık kullanılan sekmeler: Mola Saati, Hedefler, Günlük")

# ==========================================
# ÜST METRİK PANELİ
# ==========================================
su_sayisi = len([s for s in veri["su_kayitlari"] if s.get("tarih") == bugun])
toplam_kayitli_gun = len(veri["ruh_hali_kayitlari"])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📅 Bugün", datetime.date.today().strftime("%d %B"))
with col2:
    st.metric("😊 Enerji Modun", f"{bugunku_kayit['enerji']}/5" if bugunku_kayit else "Girilmedi")
with col3:
    st.metric("💧 Su Tüketimi", f"{su_sayisi} bardak")
with col4:
    st.metric("📊 Toplam Kayıtlı Gün", f"{toplam_kayitli_gun} gün")

# ==========================================
# MANUEL YAZMA HATIRLATICISI
# ==========================================
if "son_hatirlatma_zamani" not in st.session_state:
    st.session_state.son_hatirlatma_zamani = datetime.datetime.now()
if "hatirlatma_araligi" not in st.session_state:
    st.session_state.hatirlatma_araligi = 60

col_a, col_b = st.columns([3, 1])
with col_a:
    st.session_state.hatirlatma_araligi = st.slider("⏰ Kaç dakikada bir hatırlatsın?", 15, 120, st.session_state.hatirlatma_araligi, step=15)
with col_b:
    if st.button("🔄 Şimdi Sıfırla", use_container_width=True):
        st.session_state.son_hatirlatma_zamani = datetime.datetime.now()

gecen_dakika = (datetime.datetime.now() - st.session_state.son_hatirlatma_zamani).total_seconds() / 60
if gecen_dakika >= st.session_state.hatirlatma_araligi:
    st.warning("✍️ **Hatırlatma:** Bir şeyleri elle (manuel) yazmayı unutma!")
    if st.button("✅ Yazdım, hatırlatmayı sıfırla"):
        st.session_state.son_hatirlatma_zamani = datetime.datetime.now()
        st.rerun()
else:
    kalan = int(st.session_state.hatirlatma_araligi - gecen_dakika)
    st.caption(f"⏳ Bir sonraki hatırlatmaya {kalan} dakika var.")

# ==========================================
# SİGARA HATIRLATICISI
# ==========================================
if "son_sigara_hatirlatma" not in st.session_state:
    st.session_state.son_sigara_hatirlatma = datetime.datetime.now()

SIGARA_MESAJLARI = [
    "🌸 Bir sigara yerine, 3 derin nefes almaya ne dersin? Sen bundan çok daha güçlüsün.",
    "💅 Az önce mola vermiştin, şimdi biraz su içip ellerini meşgul etmeye ne dersin?",
    "🎀 Canın sıkıldıysa, sigara yerine sevdiğin bir şarkıyı açıp 2 dakika dans et.",
    "🌷 Sen harikasın, bir sigarayı erteleyebilirsin — kendine güven.",
    "🩰 Bir sonraki molada, sigara yerine küçük bir yürüyüş yapmayı dene.",
]
gecen_sigara_dakika = (datetime.datetime.now() - st.session_state.son_sigara_hatirlatma).total_seconds() / 60
if gecen_sigara_dakika >= 45:
    secilen_mesaj = SIGARA_MESAJLARI[int(datetime.datetime.now().timestamp()) % len(SIGARA_MESAJLARI)]
    st.info(secilen_mesaj)
    if st.button("💖 Gördüm, teşekkürler"):
        st.session_state.son_sigara_hatirlatma = datetime.datetime.now()
        st.rerun()

with st.expander("📊 Son 5 Günlük Vardiya Günlüğüm"):
    if veri["ruh_hali_kayitlari"]:
        for kayit in reversed(veri["ruh_hali_kayitlari"][-5:]):
            st.text(f"📅 {kayit['tarih']} | Enerji: {kayit['enerji']}/5 | Yoğunluk: {kayit['zorluk']} | Not: {kayit['not']}")
    else:
        st.write("Henüz geçmiş gün kaydı bulunmuyor.")

st.divider()

# ==========================================
# SEKMELER (Hazır Cevaplar kaldırıldı, 3 yeni sekme eklendi)
# ==========================================
sekmeler = st.tabs([
    "⏱️ Mola Saati",
    "🩸 Sağlık & Döngü Takvimi",
    "💧 Su Takibi",
    "🎧 Keyifli Anlar",
    "⏱️ Vardiya & Mesai",
    "📈 Haftalık İstatistik",
    "🎯 Hedefler & Ödüller",
    "📔 Günlük (Journal)",
])

# ------------------------------------------
# SEKME 1: MOLA SAATİ
# ------------------------------------------
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
        st.session_state.mola_baslangic_saati = simdi

    if "mola_bitis" in st.session_state:
        kalan_ms = int((st.session_state.mola_bitis - datetime.datetime.now()).total_seconds() * 1000)
        baslangic_str = st.session_state.get("mola_baslangic_saati", datetime.datetime.now()).strftime("%H:%M")
        bitis_str = st.session_state.mola_bitis.strftime("%H:%M")
        st.caption(f"🕐 Çıkış: {baslangic_str}  →  Dönüş: {bitis_str}")

        if kalan_ms > 0:
            components.html(f"""
            <div style="font-family: 'Quicksand', sans-serif; text-align:center; padding:20px; background:#161b22; border-radius:16px; border-left:5px solid #ff6a88;">
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
                            for (let i=0; i<3; i++) {{
                                setTimeout(function() {{
                                    const osc = ctx.createOscillator();
                                    const gain = ctx.createGain();
                                    osc.connect(gain); gain.connect(ctx.destination);
                                    osc.frequency.value = 880; gain.gain.value = 0.25;
                                    osc.start(); osc.stop(ctx.currentTime + 0.3);
                                }}, i * 400);
                            }}
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

    st.divider()
    st.markdown("### 🧘‍♀️ Masa Başı Mola Tavsiyesi")
    if kullanilacak_sure <= 5:
        st.info("👉 **Göz Dinlendirme (20-20-20 Kuralı):** 20 saniye boyunca en az 20 metre uzağa bak.")
    else:
        st.info("👉 **Masa Başı Esneme Zamanı:** Omuzlarını geriye çevir, boynunu esnet, derin nefes al.")

    st.divider()
    st.markdown("### 🎡 Kararsız mısın? Çarkı çevir!")
    MOLA_AKTIVITELERI = [
        "☕ Kahve/çay molası ver", "🚶 5 dakika yürüyüş yap", "🎵 Sevdiğin bir şarkıyı dinle",
        "📱 Sevdiğin biriyle kısa mesajlaş", "🧘 3 derin nefes al", "🍫 Küçük bir atıştırmalık ye",
        "🌤️ Pencereden dışarı bak", "✍️ Aklındakileri 2 satır yaz",
    ]
    if st.button("🎡 Çarkı Çevir", use_container_width=True):
        st.session_state.cark_sonucu = random.choice(MOLA_AKTIVITELERI)
    if "cark_sonucu" in st.session_state:
        st.markdown(f'<div class="rozet-kutusu" style="font-size:20px;">{st.session_state.cark_sonucu}</div>', unsafe_allow_html=True)

# ------------------------------------------
# SEKME 2: SAĞLIK & DÖNGÜ TAKVİMİ
# ------------------------------------------
with sekmeler[1]:
    st.subheader("🩸 Özel Döngü Takvimi")
    col1, col2 = st.columns(2)
    with col1:
        son_tarih = st.date_input("Son Döngü Başlangıç Tarihi", value=datetime.date.today())
        dongu_suresi = st.number_input("Ortalama Döngü Süresi (Gün)", min_value=20, max_value=45, value=28)
        semptom = st.multiselect("Bugünkü Semptomlar / Mod", ["Hafif Sancı", "Şiddetli Sancı", "Yorgunluk", "Stresli", "Tatlı Krizi", "Normal"])
    with col2:
        if st.button("🩸 Döngü Gününü Kaydet", type="primary", use_container_width=True):
            veri["regl_kayitlari"].append({"tarih": son_tarih.strftime("%d-%m-%Y"), "sure": dongu_suresi, "semptomlar": semptom})
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
                st.warning(f"Yaklaşan döneme **{kalan_gun} gün** kaldı. Molanı ona göre planla! ☕")
            elif kalan_gun == 0:
                st.error("Döngü günü bugün görünüyor! Kendine ekstra nazik davran Eda. ✨")

    st.divider()
    st.write("📂 **Geçmiş Döngü Kayıtları**")
    for r in reversed(veri["regl_kayitlari"][-5:]):
        st.text(f"📅 Başlangıç: {r['tarih']} | Döngü: {r['sure']} Gün | Semptomlar: {', '.join(r['semptomlar']) if r['semptomlar'] else 'Yok'}")

# ------------------------------------------
# SEKME 3: SU TAKİBİ
# ------------------------------------------
with sekmeler[2]:
    st.subheader("💧 Sağlık & Su Kontrolü")
    hedef_bardak = 8
    ilerleme_orani = min(su_sayisi / hedef_bardak, 1.0)
    st.progress(ilerleme_orani)

    if su_sayisi >= hedef_bardak:
        st.success(f"🎉 Harikasın Eda! Bugün {su_sayisi} bardak su içerek hedefine ulaştın! 💧")
    else:
        st.info(f"Bugün toplam **{su_sayisi} bardak** su içtin. **{hedef_bardak - su_sayisi} bardak** daha içmelisin. 😉")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💧 Bir Bardak Su İçtim", use_container_width=True, type="primary"):
            veri["su_kayitlari"].append({"tarih": bugun, "saat": datetime.datetime.now().strftime("%H:%M")})
            veri_kaydet(veri)
            st.rerun()
    with col2:
        bugunku_su_sayisi = len([s for s in veri["su_kayitlari"] if s.get("tarih") == bugun])
        if st.button("↩️ Son Girişi Geri Al", use_container_width=True, disabled=(bugunku_su_sayisi == 0)):
            for i in range(len(veri["su_kayitlari"]) - 1, -1, -1):
                if veri["su_kayitlari"][i].get("tarih") == bugun:
                    veri["su_kayitlari"].pop(i)
                    break
            veri_kaydet(veri)
            st.rerun()

    if bugunku_su_sayisi > 0:
        saatler = ", ".join([s["saat"] for s in veri["su_kayitlari"] if s["tarih"] == bugun])
        st.caption(f"Saatler: {saatler}")

# ------------------------------------------
# SEKME 4: KEYİFLİ ANLAR
# ------------------------------------------
with sekmeler[3]:
    st.subheader("🎧 Mola Anına Göre Müzik Önerisi")
    ruh_hali_secimi = st.radio("Şu an nasıl hissediyorsun?", ["😴 Yorgunum", "⚡ Enerji lazım", "😊 Keyifliyim", "🧠 Odaklanmam lazım"], horizontal=True)

    SARKI_ONERILERI = {
        "😴 Yorgunum": [("Norah Jones", "Come Away With Me"), ("Bon Iver", "Skinny Love"), ("Türkçe Lo-fi", "Chillhop Türkçe")],
        "⚡ Enerji lazım": [("Duman", "Eyvallah"), ("Dua Lipa", "Levitating"), ("Mor ve Ötesi", "Bir Derdim Var")],
        "😊 Keyifliyim": [("Kenan Doğulu", "Aşk Kadın Ruhudur"), ("Feel Good Mix", "Spotify Feel Good Friday")],
        "🧠 Odaklanmam lazım": [("Lofi Beats", "Spotify Lofi Beats"), ("Peaceful Piano", "Spotify Peaceful Piano")],
    }
    for sanatci, sarki in SARKI_ONERILERI[ruh_hali_secimi]:
        st.write(f"🎵 **{sanatci}** — {sarki}")

    if st.button("🔀 Sürpriz Şarkı"):
        tum_sarkilar = [s for liste in SARKI_ONERILERI.values() for s in liste]
        st.success(f"🎲 {random.choice(tum_sarkilar)[0]} — {random.choice(tum_sarkilar)[1]}")

    st.divider()
    st.subheader("✨ Küçük Bir Şey")
    KUCUK_SEYLER = [
        "Bugün kendine güzel bir şey söyle: 'Elimden geleni yapıyorum ve bu yeterli.' 💛",
        "5 dakikalığına telefonunu bırak, pencereden dışarı bak.",
        "Sevdiğin bir fotoğrafa bak, gülümse.",
        "Bir sonraki molada sevdiğin bir atıştırmalığı kendine ayır.",
    ]
    if st.button("💫 Bana Küçük Bir Şey Söyle"):
        st.info(random.choice(KUCUK_SEYLER))

# ------------------------------------------
# SEKME 5: VARDİYA & MESAİ
# ------------------------------------------
with sekmeler[4]:
    st.subheader("⏱️ Anlık Mesai ve Vardiya Takip Paneli")
    col_inputs1, col_inputs2 = st.columns(2)
    with col_inputs1:
        mesai_baslangic = st.time_input("🚀 Mesai Başlangıç Saati", datetime.time(9, 0))
        toplam_mola_sure = st.number_input("☕ Toplam Mola Süresi (Dakika)", min_value=0, value=60, step=5)
    with col_inputs2:
        mesai_bitis = st.time_input("🚪 Mesai Bitiş Saati", datetime.time(18, 0))
        su_an = st.time_input("🕒 Şu Anki Saat", datetime.datetime.now().time())

    gunun_tarihi = datetime.date.today()
    dt_baslangic = datetime.datetime.combine(gunun_tarihi, mesai_baslangic)
    dt_bitis = datetime.datetime.combine(gunun_tarihi, mesai_bitis)
    dt_su_an = datetime.datetime.combine(gunun_tarihi, su_an)
    if dt_bitis <= dt_baslangic:
        dt_bitis += datetime.timedelta(days=1)

    toplam_mesai_saniye = (dt_bitis - dt_baslangic).total_seconds()

    if dt_su_an < dt_baslangic:
        kalan_sure = dt_baslangic - dt_su_an
        st.info(f"⏳ Mesainin başlamasına **{kalan_sure.seconds // 3600} saat {(kalan_sure.seconds % 3600) // 60} dakika** var.")
        st.progress(0.0)
    elif dt_su_an >= dt_bitis:
        st.success("🎉 Mesai bitti! Harika bir iş çıkardın Eda!")
        st.progress(1.0)
    else:
        gecen_saniye = (dt_su_an - dt_baslangic).total_seconds()
        kalan_saniye = (dt_bitis - dt_su_an).total_seconds()
        yuzde = min(max(gecen_saniye / toplam_mesai_saniye, 0.0), 1.0)

        c1, c2, c3 = st.columns(3)
        c1.metric("⏱️ Geçen Süre", f"{int(gecen_saniye // 3600)}s {int((gecen_saniye % 3600) // 60)}dk")
        c2.metric("⏳ Kalan Süre", f"{int(kalan_saniye // 3600)}s {int((kalan_saniye % 3600) // 60)}dk")
        c3.metric("🎯 İlerleme", f"%{int(yuzde * 100)}")
        st.progress(yuzde)

        if yuzde < 0.25: st.write("🚀 Gün yeni başlıyor!")
        elif yuzde < 0.50: st.write("⚡ Öğle arasına az kaldı!")
        elif yuzde < 0.75: st.write("☕ Yarı yoldasın!")
        else: st.write("✨ Son düzlük!")

# ------------------------------------------
# SEKME 6: HAFTALIK İSTATİSTİK (YENİ)
# ------------------------------------------
with sekmeler[5]:
    st.subheader("📈 Son 7 Günün Trendi")
    import pandas as pd
    son_kayitlar = veri["ruh_hali_kayitlari"][-7:]

    if len(son_kayitlar) >= 2:
        grafik_verisi = pd.DataFrame({"Tarih": [k["tarih"] for k in son_kayitlar], "Enerji": [k["enerji"] for k in son_kayitlar]}).set_index("Tarih")
        st.line_chart(grafik_verisi)

        ortalama = sum(k["enerji"] for k in son_kayitlar) / len(son_kayitlar)
        col1, col2 = st.columns(2)
        col1.metric("7 Günlük Ortalama Enerji", f"{ortalama:.1f} / 5")
        en_dusuk = min(son_kayitlar, key=lambda k: k["enerji"])
        col2.metric("En Yorucu Gün", en_dusuk["tarih"])

        if ortalama < 2.5:
            st.warning("Son günlerde enerjin düşük görünüyor, kendine biraz daha zaman ayırmayı düşünebilirsin. 💛")
        elif ortalama >= 4:
            st.success("Son günler harika geçiyor! 🌟")
    else:
        st.info("Trend görebilmek için en az 2 günlük kayıt gerekiyor.")

    st.divider()
    st.subheader("💧 Haftalık Su Ortalaması")
    son_7_gun = [(datetime.date.today() - datetime.timedelta(days=i)).strftime("%d-%m-%Y") for i in range(7)]
    su_gunluk = {gun: len([s for s in veri["su_kayitlari"] if s["tarih"] == gun]) for gun in son_7_gun}
    su_df = pd.DataFrame({"Tarih": list(su_gunluk.keys()), "Bardak": list(su_gunluk.values())}).set_index("Tarih")
    st.bar_chart(su_df)

# ------------------------------------------
# SEKME 7: HEDEFLER & ÖDÜLLER (YENİ)
# ------------------------------------------
with sekmeler[6]:
    st.subheader("🎯 Bugünün Küçük Hedefleri")

    if bugun not in veri["hedefler"]:
        veri["hedefler"][bugun] = {
            "8 bardak su iç": False,
            "3 kısa mola yap": False,
            "Öğle molasında ekrandan uzaklaş": False,
            "Kendine güzel bir şey söyle": False,
        }

    degisti = False
    for hedef_adi in list(veri["hedefler"][bugun].keys()):
        mevcut = veri["hedefler"][bugun][hedef_adi]
        yeni = st.checkbox(hedef_adi, value=mevcut, key=f"hedef_{hedef_adi}")
        if yeni != mevcut:
            veri["hedefler"][bugun][hedef_adi] = yeni
            degisti = True

    if degisti:
        veri_kaydet(veri)

    tamamlanan = sum(veri["hedefler"][bugun].values())
    toplam = len(veri["hedefler"][bugun])
    st.progress(tamamlanan / toplam)
    st.caption(f"{tamamlanan}/{toplam} hedef tamamlandı")

    if tamamlanan == toplam:
        rozet_adi = f"🏆 Mükemmel Gün — {bugun}"
        if rozet_adi not in veri["rozetler_kazanildi"]:
            veri["rozetler_kazanildi"].append(rozet_adi)
            veri_kaydet(veri)
        st.balloons()
        st.success("Bugün tüm hedefleri tamamladın! 🏆")

    st.divider()
    st.subheader("🏅 Kazanılan Rozetler")
    if veri["rozetler_kazanildi"]:
        for rozet in reversed(veri["rozetler_kazanildi"][-10:]):
            st.markdown(f'<div class="rozet-kutusu">{rozet}</div>', unsafe_allow_html=True)
    else:
        st.info("Henüz rozet kazanılmadı, ilk mükemmel günü tamamla!")

# ------------------------------------------
# SEKME 8: GÜNLÜK / JOURNAL (YENİ — Hazır Cevaplar'ın yerine)
# ------------------------------------------
with sekmeler[7]:
    st.subheader("📔 Bugün nasıl geçti? Birkaç cümle yaz")
    st.caption("Bu tamamen kişisel alanın — kimse görmüyor, sadece kendi bilgisayarında saklanıyor.")

    gunluk_yazi = st.text_area("Bugünün notu", height=150, placeholder="Bugün neler oldu, ne hissettin...")
    if st.button("💾 Günlüğe Kaydet", type="primary"):
        if gunluk_yazi.strip():
            veri["gunluk_yazilar"].append({
                "tarih": bugun,
                "saat": datetime.datetime.now().strftime("%H:%M"),
                "yazi": gunluk_yazi.strip()
            })
            veri_kaydet(veri)
            st.success("Kaydedildi 💛")
            st.rerun()

    st.divider()
    st.subheader("📖 Geçmiş Yazılar")
    if veri["gunluk_yazilar"]:
        for kayit in reversed(veri["gunluk_yazilar"][-10:]):
            with st.expander(f"📅 {kayit['tarih']} — {kayit['saat']}"):
                st.write(kayit["yazi"])
    else:
        st.info("Henüz bir günlük yazısı yok.")

st.write("---")
st.caption("🐾 *Eda için tasarlanan, sıfır maliyetli kişisel destek paneli.*")
