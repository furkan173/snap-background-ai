import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground AI v3.1", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
os.environ["FAL_KEY"] = FAL_KEY

SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"

# --- SESSION STATE (Giriş Durumu Kontrolü) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# --- YARDIMCI FONKSİYONLAR ---
def login_user(email, password):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    data = {"email": email, "password": password}
    response = requests.post(url, headers=headers, json=data)
    return response

def signup_user(email, password):
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    data = {"email": email, "password": password}
    return requests.post(url, headers=headers, json=data)

def get_credits(user_id):
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
    res = requests.get(f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}", headers=headers).json()
    if res:
        return res[0]['credits']
    return 0

# --- GİRİŞ / KAYIT EKRANI ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        email = st.text_input("E-posta")
        pwd = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            res = login_user(email, pwd)
            if res.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_id = res.json()['user']['id']
                st.rerun()
            else:
                st.error("Giriş başarısız. Bilgilerinizi kontrol edin.")
                
    with tab2:
        new_email = st.text_input("Yeni E-posta")
        new_pwd = st.text_input("Yeni Şifre (En az 6 karakter)")
        if st.button("Kayıt Ol"):
            res = signup_user(new_email, new_pwd)
            if res.status_code == 200 or res.status_code == 201:
                st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
            else:
                st.error("Kayıt sırasında bir hata oluştu.")
    st.stop()

# --- ANA UYGULAMA (Giriş Yapıldıysa) ---
user_id = st.session_state.user_id
current_credits = get_credits(user_id)

with st.sidebar:
    st.title("👤 Profil")
    st.write(f"Kullanıcı: {st.session_state.user_email}")
    st.metric("Kalan Kredi", current_credits)
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.rerun()

st.title("📸 SnapBackground AI - v3.1")

if current_credits <= 0:
    st.warning("⚠️ Krediniz bitmiştir.")
else:
    uploaded_file = st.file_uploader("Ürünü yükleyin", type=["jpg", "png"])
    if uploaded_file:
        user_prompt = st.text_input("Arka plan tarifi (İngilizce)", "luxury marble table")
        if st.button("Sihri Başlat 🚀"):
            with st.spinner("İşleniyor..."):
                # Buraya bir önceki adımdaki resim oluşturma kodlarını koyacağız 
                # Ama önce giriş yapabildiğimizi görelim!
                st.info("Sistem hazır, kredin var! Giriş başarılı.")
