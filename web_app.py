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

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- YARDIMCI FONKSİYONLAR ---
def login_user(email, password):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    data = {"email": email, "password": password}
    return requests.post(url, headers=headers, json=data)

def signup_user(email, password):
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    data = {"email": email, "password": password}
    return requests.post(url, headers=headers, json=data)

def get_credits(user_id):
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
    res = requests.get(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=headers).json()
    if res:
        return res[0]['krediler']
    return 0

def decrease_credit(user_id, current_val):
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    new_val = max(0, current_val - 1)
    requests.patch(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=headers, json={"krediler": new_val})
    return new_val

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with tab1:
        e = st.text_input("E-posta")
        p = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            res = login_user(e, p)
            if res.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.user_email = e
                st.session_state.user_id = res.json()['user']['id']
                st.rerun()
            else: st.error("Hatalı giriş.")
    with tab2:
        ne = st.text_input("Yeni E-posta")
        np = st.text_input("Şifre (min 6)")
        if st.button("Kayıt Ol"):
            if signup_user(ne, np).status_code in [200, 201]: st.success("Başarılı! Giriş yapın.")
            else: st.error("Hata oluştu.")
    st.stop()

# --- ANA UYGULAMA ---
user_id = st.session_state.user_id
current_credits = get_credits(user_id)

with st.sidebar:
    st.title("👤 Profil")
    st.write(f"**{st.session_state.user_email}**")
    st.metric("Kalan Kredi", current_credits)
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.rerun()

st.title("📸 SnapBackground AI - Profesyonel Stüdyo")

if current_credits <= 0:
    st.error("❌ Krediniz bitmiştir.")
else:
    uploaded_file = st.file_uploader("Ürünü yükleyin", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        user_prompt = st.text_input("Arka plan tarifi (İngilizce):", "luxury marble table, studio lighting")
        if st.button("Sihri Başlat (1 Kredi) 🚀"):
            with st.spinner("Yapay zeka görseli hazırlıyor..."):
                try:
                    # 1. Resim Yükleme (Supabase Storage)
                    f_name = f"{int(time.time())}_{uploaded_file.name}"
                    up_url = f"{SUPABASE_URL}/storage/v1/object/photos/{f_name}"
                    headers_up = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": uploaded_file.type}
                    requests.post(up_url, data=uploaded_file.getvalue(), headers=headers_up)
                    public_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_name}"

                    # 2. Fal.ai Bağlantısı
                    result = fal_client.subscribe(
                        "fal-ai/fooocus/image-prompt",
                        arguments={
                            "prompt": f"Professional product photography, {user_prompt}, 8k highly detailed",
                            "image_prompt_1": {"image_url": public_url},
                            "image_prompt_model_1": "face_swap",
                            "image_prompt_strength": 0.85
                        }
                    )
                    
                    if result and 'images' in result:
                        st.image(result['images'][0]['url'], caption="AI Tarafından Oluşturuldu", use_container_width=True)
                        # 3. Krediyi Düşür
                        decrease_credit(user_id, current_credits)
                        st.success("İşlem Başarılı! Krediniz düştü.")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")
