import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground AI v3.4", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"

os.environ["FAL_KEY"] = FAL_KEY

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "generated_image" not in st.session_state: st.session_state.generated_image = None

# --- VERİTABANI FONKSİYONLARI ---
def login_user(email, password):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json={"email": email, "password": password})

def get_credits(user_id):
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=headers).json()
        return res[0].get('krediler', 0) if res else 0
    except: return 0

def decrease_credit(user_id, current_val):
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    new_val = max(0, current_val - 1)
    requests.patch(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=headers, json={"krediler": new_val})
    return new_val

# --- GİRİŞ ---
if not st.session_state.logged_in:
    st.title("📸 SnapBackground Giriş")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        res = login_user(e, p)
        if res.status_code == 200:
            st.session_state.logged_in = True
            st.session_state.user_id = res.json()['user']['id']
            st.session_state.user_email = e
            st.rerun()
        else: st.error("Giriş başarısız.")
    st.stop()

# --- UYGULAMA ---
user_id = st.session_state.user_id
current_credits = get_credits(user_id)

with st.sidebar:
    st.title("👤 Profil")
    st.metric("Kalan Kredi", current_credits)
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.rerun()

st.title("📸 SnapBackground AI - Profesyonel Stüdyo")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Ürünü yükleyin", type=["jpg", "png", "jpeg"])
    user_prompt = st.text_input("Arka plan tarifi:", "luxury marble table")
    
    if st.button("Sihri Başlat (1 Kredi) 🚀") and uploaded_file:
        if current_credits > 0:
            with st.spinner("Görsel hazırlanıyor..."):
                try:
                    # 1. Resim Yükleme
                    f_name = f"{int(time.time())}_{uploaded_file.name}"
                    up_url = f"{SUPABASE_URL}/storage/v1/object/photos/{f_name}"
                    headers_up = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": uploaded_file.type}
                    requests.post(up_url, data=uploaded_file.getvalue(), headers=headers_up)
                    p_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_name}"

                    # 2. AI Çalıştırma
                    result = fal_client.subscribe(
                        "fal-ai/fooocus/image-prompt",
                        arguments={
                            "prompt": f"Professional product photography, {user_prompt}, 8k",
                            "image_prompt_1": {"image_url": p_url},
                            "image_prompt_model_1": "face_swap",
                            "image_prompt_strength": 0.85
                        }
                    )
                    
                    if result and 'images' in result:
                        st.session_state.generated_image = result['images'][0]['url']
                        decrease_credit(user_id, current_credits)
                        st.rerun() # Kredinin güncellenmesi için yenile
                except Exception as e:
                    st.error(f"Hata: {e}")
        else:
            st.warning("Krediniz yetersiz!")

with col2:
    st.subheader("✨ Sonuç")
    if st.session_state.generated_image:
        st.image(st.session_state.generated_image, use_container_width=True)
        st.success("Görsel başarıyla oluşturuldu! Sağ tıklayıp kaydedebilirsiniz.")
        if st.button("Yeni Görsel Oluştur 🔄"):
            st.session_state.generated_image = None
            st.rerun()
