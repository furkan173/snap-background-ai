import streamlit as st
import requests
import time
import base64
from openai import OpenAI

# --- SİSTEM AYARLARI ---
st.set_page_config(page_title="Etsy SEO Magic Pro v2.0", layout="wide")

# OpenAI API anahtarını sistem ayarlarından güvenli şekilde alıyoruz
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"] 
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"

client = OpenAI(api_key=OPENAI_API_KEY)

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
    st.title("📦 Etsy SEO Magic Pro (GPT-4o Edition)")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
    st.stop()

# --- ANA KONTROL PANELİ ---
user_id = st.session_state.user_id
current_c = get_credits(user_id)

with st.sidebar:
    st.title("💎 PRO Satıcı")
    st.metric("Kalan Kredi", current_c)
    
    # --- ÖDEME BÖLÜMÜ ---
    st.markdown("---")
    st.subheader("Kredi Yükle")
    
    checkout_url = "https://getsnapbackground.lemonsqueezy.com/checkout/buy/a35adaa5-735c-4ffb-936d-442576c4c753"
    
    # Şık bir satın al butonu
    st.markdown(f'''
        <a href="{checkout_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #FF4B4B; color: white; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px; transition: 0.3s; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
                🔥 100 Kredi Satın Al
            </div>
        </a>
    ''', unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; font-size: 12px; color: gray; margin-top: 10px;'>Güvenli ödeme Lemon Squeezy ile sağlanmaktadır.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("Güvenli Çıkış"): 
        st.session_state.logged_in = False
        st.rerun()

st.title("🚀 Etsy SEO & Tanım Uzmanı")

col1, col2 = st.columns([1, 1.5])

with col1:
    up = st.file_uploader("Ürün Fotoğrafı Yükle", type=["jpg", "png", "jpeg"])
    lang = st.selectbox("Çıktı Dili", ["English", "Turkish"])
    
    if st.button("SEO Analizini Başlat ✨") and up:
        if current_c > 0:
            with st.spinner("GPT-4o Vision ürünü inceliyor..."):
                try:
                    # Fotoğrafı Base64 formatına çevir (OpenAI için en hızlı yol)
                    base64_image = base64.b64encode(up.getvalue()).decode('utf-8')

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": f"You are a professional Etsy SEO Expert. Analyze this product and provide: 1. A catchy high-ranking Title. 2. 13 distinct SEO Tags (comma-separated). 3. A professional description. Language: {lang}"},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ],
                            }
                        ],
                        max_tokens=1000,
                    )

                    output = response.choices[0].message.content
                    if output:
                        st.session_state.seo_data = output
                        use_credit(user_id, current_c)
                        st.rerun()
                except Exception as ex:
                    st.error(f"OpenAI Hatası: {ex}")
        else:
            st.warning("Krediniz kalmadı.")

with col2:
    st.subheader("📝 GPT-4o SEO Analizi")
    if st.session_state.seo_data:
        st.text_area("Kopyalamaya Hazır Veri", st.session_state.seo_data, height=550)
        if st.button("Yeni Analiz 🔄"):
            st.session_state.seo_data = None
            st.rerun()
    else:
        st.info("Sonuçlar burada listelenecek.")
