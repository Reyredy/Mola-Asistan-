import streamlit as st
import json
import os
import datetime
import pandas as pd

st.set_page_config(page_title="Detaylı Rapor", page_icon="📊", layout="wide")

st.title("📊 Detaylı Rapor ve Trendler")
st.caption("Zaman içindeki enerji, zorluk ve su tüketim trendlerin")

VERI_DOSYASI = "mola_verileri.json"

def veri_yukle():
    if os.path.exists(VERI_DOSYASI):
        with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ruh_hali_kayitlari": [], "hazir_cevaplar": [], "vardiya_notlari": [], "su_kayitlari": []}

veri = veri_yukle()
kayitlar = veri.get("ruh_hali_kayitlari", [])

if not kayitlar:
    st.info("Henüz yeterli veri yok. Ana sayfadan birkaç gün kayıt girdikten sonra buraya dön.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
ortalama_enerji = sum(k["enerji"] for k in kayitlar) / len(kayitlar)
en_iyi_gun = max(kayitlar, key=lambda k: k["enerji"])
en_kotu_gun = min(kayitlar, key=lambda k: k["enerji"])

with col1:
    st.metric("Ortalama Enerji", f"{ortalama_enerji:.1f} / 5")
with col2:
    st.metric("Toplam Kayıtlı Gün", len(kayitlar))
with col3:
    st.metric("En İyi Gün", f"{en_iyi_gun['tarih']} ({en_iyi_gun['enerji']}/5)")
with col4:
    st.metric("En Zor Gün", f"{en_kotu_gun['tarih']} ({en_kotu_gun['enerji']}/5)")

st.divider()

st.subheader("📈 Zaman İçinde Enerji Seviyesi")
grafik_verisi = pd.DataFrame({
    "Tarih": [k["tarih"] for k in kayitlar],
    "Enerji": [k["enerji"] for k in kayitlar]
})
grafik_verisi = grafik_verisi.set_index("Tarih")
st.line_chart(grafik_verisi)

st.subheader("📅 Haftanın Günlerine Göre Ortalama Enerji")
gun_toplam = {}
gun_sayisi = {}
for k in kayitlar:
    gun = k.get("gun", "Bilinmiyor")
    gun_toplam[gun] = gun_toplam.get(gun, 0) + k["enerji"]
    gun_sayisi[gun] = gun_sayisi.get(gun, 0) + 1

gun_ortalamalari = {gun: gun_toplam[gun] / gun_sayisi[gun] for gun in gun_toplam}

if gun_ortalamalari:
    gun_df = pd.DataFrame({
        "Gün": list(gun_ortalamalari.keys()),
        "Ortalama Enerji": list(gun_ortalamalari.values())
    }).set_index("Gün")
    st.bar_chart(gun_df)
    en_yorucu_gun = min(gun_ortalamalari, key=gun_ortalamalari.get)
    st.warning(f"⚠️ Veriye göre en yorucu günün: **{en_yorucu_gun}** — bu gün için ekstra mola planlamak faydalı olabilir.")

st.subheader("🎯 Vardiya Zorluk Dağılımı")
zorluk_sayaci = {}
for k in kayitlar:
    z = k.get("zorluk", "Belirtilmemiş")
    zorluk_sayaci[z] = zorluk_sayaci.get(z, 0) + 1

if zorluk_sayaci:
    zorluk_df = pd.DataFrame({
        "Zorluk": list(zorluk_sayaci.keys()),
        "Gün Sayısı": list(zorluk_sayaci.values())
    }).set_index("Zorluk")
    st.bar_chart(zorluk_df)

st.divider()
st.subheader("📝 Tüm Notlar (kronolojik)")
notlu_kayitlar = [k for k in kayitlar if k.get("not")]
if notlu_kayitlar:
    for k in reversed(notlu_kayitlar):
        st.write(f"**{k['tarih']}**: {k['not']}")
else:
    st.info("Henüz not eklenmiş bir kayıt yok.")