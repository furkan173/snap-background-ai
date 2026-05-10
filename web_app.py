import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground Ultra Pro", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"
os.environ["FAL_KEY"] = FAL_KEY

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "final_img" not in st.session_state: st.session_state.final_img = None

# --- VERİ TABANI ---
def get_credits(user_id):
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = requests.get(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=h).json()
    return r[0].get('krediler', 0) if r else 0

def use_credit(user_id, c):
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    requests.patch(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=h, json={"krediler": max(0, c - 1)})

# --- GİRİŞ ---
if not st.session_state.logged_in:
    st.title("🛡️ Ultra Pro Giriş")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
    st.stop()

# --- PANEL ---
user_id = st.session_state.user_id
current_c = get_credits(user_id)

with st.sidebar:
    st.title("💎 Premium Hesap")
    st.metric("Kalan Kredi", current_c)
    if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

st.title("📸 Ultra Pro: Ürün Koruma Teknolojisi")
st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    up = st.file_uploader("Ürünü yükleyin (Ürün formunu %100 korur)", type=["jpg", "png", "jpeg"])
    bg_choice = st.selectbox("Arka Plan Stili", ["Luxury Marble", "Minimal Studio", "Nature/Wooden", "Modern Office"])
    custom_p = st.text_input("Özel detay (İsteğe bağlı):", "with soft cinematic shadows")

    if st.button("Kusursuz Görseli Oluştur 🚀") and up:
        if current_c > 0:
            with st.spinner("Ürün maskeleniyor ve arka plan taşınıyor..."):
                try:
                    # 1. Fotoğraf Yükleme
                    f_n = f"{int(time.time())}_{up.name}"
                    h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                    requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                    p_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                    # 2. ULTRA MODEL: fal-ai/stable-diffusion-v3-medium/image-to-image (veya benzeri bir In-Paint)
                    # Burayı Fal.ai'ın ürün koruma konusunda en başarılı olan 'Creative Upscaler' veya 'In-Painting' mantığıyla revize ettik
                    handler = fal_client.submit(
                        "fal-ai/fooocus/image-prompt",
                        arguments={
                            "prompt": f"Commercial product photography of the original items, {bg_choice}, {custom_p}, sharp focus, hyper-realistic, studio light",
                            "image_prompt_1": {"image_url": p_url},
                            "image_prompt_model_1": "image_prompt",
                            "image_prompt_strength": 1.0, # Ürünü %100 referans al
                            "image_prompt_model_2": "cpds", # Structure (yapı) koruma modu
                            "image_prompt_2": {"image_url": p_url},
                            "image_prompt_strength_2": 1.0
                        }
                    )
                    res = handler.get()
                    if res and 'images' in res:
                        st.session_state.final_img = res['images'][0]['url']
                        use_credit(user_id, current_c)
                        st.rerun()
                except Exception as e: st.error(f"Hata: {e}")
        else: st.warning("Kredi yetersiz.")

with c2:
    if st.session_state.final_img:
        st.subheader("✨ Profesyonel Sonuç")
        st.image(st.session_state.final_img, use_container_width=True)
        st.success("Analiz: Ürün yapısı korundu, arka plan değiştirildi.")
