import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="Etsy SEO Magic AI", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"
os.environ["FAL_KEY"] = FAL_KEY

if "logged_in" not in st.session_state: st.session_state.logged_in = False

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
    st.title("📦 Etsy SEO Magic Giriş")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
    st.stop()

# --- PANEL ---
current_c = get_credits(st.session_state.user_id)
with st.sidebar:
    st.title("💎 Satıcı Paneli")
    st.metric("Kalan Kredi", current_c)
    if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

st.title("🚀 Etsy SEO & Tanım Yazıcı")
st.markdown("Fotoğrafını yükle, Etsy'de en üst sıralara çıkmanı sağlayacak SEO paketini al.")

c1, c2 = st.columns([1, 1.5])

with c1:
    up = st.file_uploader("Ürün Fotoğrafı", type=["jpg", "png", "jpeg"])
    language = st.selectbox("Çıktı Dili", ["English", "Turkish"])
    
    if st.button("SEO Analizini Başlat (1 Kredi) ✨") and up:
        if current_c > 0:
            status = st.empty()
            try:
                # 1. Fotoğrafı Yükleme
                status.text("1/2: Ürün analiz ediliyor...")
                f_n = f"{int(time.time())}_{up.name}"
                h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                img_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                # 2. Vision AI Analizi (HIZLI MODEL: fal-ai/moondream)
                status.text("2/2: Turbo analiz başlatıldı, saniyeler içinde hazır...")
                
                with st.spinner("Etsy SEO Uzmanı verileri hazırlıyor..."):
                    result = fal_client.subscribe("fal-ai/moondream/batched", arguments={
                        "inputs": [
                            {
                                "image_url": img_url,
                                "prompt": f"Act as an Etsy SEO Expert. Look at this product and write: 1. A high-ranking Etsy Title. 2. 13 Tags (comma-separated). 3. A short professional description. Language: {language}"
                            }
                        ]
                    })

                    # Moondream batched modelinde çıktı listesi döner
                    if result and 'outputs' in result:
                        output_text = result['outputs'][0]
                        st.session_state.seo_output = output_text
                        use_credit(st.session_state.user_id, current_c)
                        st.rerun()
                    else:
                        st.error("Model cevap vermedi, lütfen tekrar deneyin.")
                
               
                
                
                

                
      

with c2:
    st.subheader("📝 SEO Sonuçları")
    if "seo_output" in st.session_state:
        st.text_area("Kopyalamaya Hazır Çıktı:", st.session_state.seo_output, height=500)
        st.success("Analiz tamamlandı! Bu bilgileri Etsy mağazana yapıştırabilirsin.")
    else:
        st.info("Lütfen bir fotoğraf yükleyip analizi başlatın.")
