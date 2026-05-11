import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="Etsy SEO Magic Pro v1.4", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"
os.environ["FAL_KEY"] = FAL_KEY

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "seo_data" not in st.session_state: st.session_state.seo_data = None

# --- VERİ TABANI ---
def get_credits(user_id):
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=h).json()
        return r[0].get('krediler', 0) if r else 0
    except: return 0

def use_credit(user_id, c):
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    requests.patch(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=h, json={"krediler": max(0, c - 1)})

# --- GİRİŞ ---
if not st.session_state.logged_in:
    st.title("📦 Etsy SEO Magic Pro")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
    st.stop()

# --- PANEL ---
user_id = st.session_state.user_id
current_c = get_credits(user_id)

with st.sidebar:
    st.title("💎 PRO Satıcı")
    st.metric("Kredi", current_c)
    if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

st.title("🚀 Etsy SEO & Tanım Uzmanı")
st.markdown("Profesyonel e-ticaret analizi için ürün fotoğrafınızı yükleyin.")

col1, col2 = st.columns([1, 1.5])

with col1:
    up = st.file_uploader("Ürün Fotoğrafı", type=["jpg", "png", "jpeg"])
    lang = st.selectbox("Çıktı Dili", ["English", "Turkish"])
    
    if st.button("SEO Paketini Oluştur ✨") and up:
        if current_c > 0:
            with st.spinner("AI ürün detaylarını ve SEO fırsatlarını analiz ediyor..."):
                try:
                    f_n = f"{int(time.time())}_{up.name}"
                    h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                    requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                    img_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                    # GÜNCEL STABİL VISION MODELİ: fuyu-vlm
                    # Not: Bu model görseli hızlı analiz eder ve açıklayıcıdır.
                    prompt = f"Act as an Etsy SEO Expert. Detail this product: 1. Etsy Title. 2. 13 Tags. 3. Description. Language: {lang}"

                    result = fal_client.subscribe("fal-ai/fuyu-vlm", arguments={
                        "image_url": img_url,
                        "prompt": prompt
                    })

                    # Sonucu almak için en kapsamlı kontrol
                    output = result.get('output') or result.get('description') or result.get('data')
                    if output:
                        st.session_state.seo_data = output
                        use_credit(user_id, current_c)
                        st.rerun()
                    else:
                        st.error("Model çalıştı ama veri dönmedi. Lütfen tekrar deneyin.")

                except Exception as ex:
                    st.error(f"Bağlantı Hatası: {ex}")
        else:
            st.warning("Krediniz kalmadı.")

with col2:
    st.subheader("📝 Analiz Sonuçları")
    if st.session_state.seo_data:
        st.info("Sonuçlar hazır! Kopyalayıp Etsy mağazanızda kullanabilirsiniz.")
        st.text_area("SEO Paketi", st.session_state.seo_data, height=500)
        if st.button("Yeni Analiz 🔄"):
            st.session_state.seo_data = None
            st.rerun()
    else:
        st.info("Analiz sonuçları burada detaylı olarak listelenecek.")
