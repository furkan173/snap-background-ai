import streamlit as st
import fal_client
import requests
import time
import os

# --- SİSTEM AYARLARI ---
st.set_page_config(page_title="Etsy SEO Magic Pro v1.9", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"
os.environ["FAL_KEY"] = FAL_KEY

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "seo_data" not in st.session_state: st.session_state.seo_data = None

# --- VERİ TABANI FONKSİYONLARI ---
def get_credits(user_id):
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=h).json()
        return r[0].get('krediler', 0) if r else 0
    except: return 0

def use_credit(user_id, c):
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    requests.patch(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=h, json={"krediler": max(0, c - 1)})

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.title("📦 Etsy SEO Magic Pro")
    st.info("Lütfen mağaza sahibi hesabınızla giriş yapın.")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
        else:
            st.error("Giriş başarısız. Bilgilerinizi kontrol edin.")
    st.stop()

# --- ANA KONTROL PANELİ ---
user_id = st.session_state.user_id
current_c = get_credits(user_id)

with st.sidebar:
    st.title("💎 Satıcı Paneli")
    st.metric("Kalan Kredi", current_c)
    if st.button("Güvenli Çıkış"): 
        st.session_state.logged_in = False
        st.rerun()

st.title("🚀 Etsy SEO & Tanım Uzmanı")
st.markdown("Ürün fotoğrafını yükleyin; GPT-4o ve Claude destekli sistemimiz SEO paketinizi hazırlasın.")

col1, col2 = st.columns([1, 1.5])

with col1:
    up = st.file_uploader("Ürün Fotoğrafı (JPG/PNG)", type=["jpg", "png", "jpeg"])
    lang = st.selectbox("Sonuç Dili", ["English", "Turkish"])
    
    if st.button("SEO Analizini Başlat ✨") and up:
        if current_c > 0:
            with st.spinner("AI dünyasının en iyi vision modellerine bağlanılıyor..."):
                try:
                    # 1. Fotoğrafı Supabase Storage'a Yükle
                    f_n = f"{int(time.time())}_{up.name}"
                    h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                    requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                    img_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                    # 2. OpenRouter Vision API Çağrısı (v1.9 Kesinleşmiş Yol)
                    result = fal_client.run("fal-ai/openrouter/vision", arguments={
                        "prompt": f"Act as an Etsy SEO Expert. Analyze this product image. Provide: 1. A catchy high-ranking Title. 2. 13 distinct SEO Tags (comma-separated). 3. A professional description with features/benefits. Language: {lang}",
                        "image_url": img_url
                    })

                    # 3. Sonuç Yakalama
                    output = ""
                    if isinstance(result, dict):
                        output = result.get('output', {}).get('text') or result.get('text') or result.get('output')

                    if output:
                        st.session_state.seo_data = output
                        use_credit(user_id, current_c)
                        st.rerun()
                    else:
                        st.error("Model çalıştı ancak anlamlı bir metin dönmedi.")

                except Exception as ex:
                    st.error(f"Bağlantı Hatası: {ex}. Lütfen API model ismini kontrol edin.")
        else:
            st.warning("İşlem için yeterli krediniz kalmadı.")

with col2:
    st.subheader("📝 Profesyonel SEO Çıktısı")
    if st.session_state.seo_data:
        st.info("Aşağıdaki verileri Etsy mağazanızdaki ilgili alanlara kopyalayıp yapıştırabilirsiniz.")
        st.text_area("Kopyalamaya Hazır Paket", st.session_state.seo_data, height=550)
        if st.button("Yeni Ürün Analiz Et 🔄"):
            st.session_state.seo_data = None
            st.rerun()
    else:
        st.info("Fotoğraf yükledikten sonra analiz sonuçları burada görünecek.")
