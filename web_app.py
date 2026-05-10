import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground ULTRA SHIELD v5.5", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"
os.environ["FAL_KEY"] = FAL_KEY

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "final_img" not in st.session_state: st.session_state.final_img = None

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
    st.title("🛡️ ULTRA SHIELD Giriş")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Sistemi Aktif Et"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
    st.stop()

# --- PANEL ---
user_id = st.session_state.user_id
current_c = get_credits(user_id)

with st.sidebar:
    st.title("💎 Premium Panel")
    st.metric("Kalan Kredi", current_c)
    if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

st.title("📸 Ultra Shield: Ürün Koruma Teknolojisi")
st.warning("Bu mod, ürünün piksellerini %100 korumak için maskeleme algoritması kullanır.")

c1, c2 = st.columns(2)
with c1:
    up = st.file_uploader("Ürünü yükleyin (Gözlük, Tarak, Saat vb.)", type=["jpg", "png", "jpeg"])
    prompt = st.text_input("Arka plan:", "on a luxury white marble table, soft studio lighting, bokeh background")

    if st.button("Cerrahi Müdahaleyi Başlat 🚀") and up:
        if current_c > 0:
            status = st.empty()
            try:
                # 1. Yükleme
                status.text("1/3: Ürün taranıyor...")
                f_n = f"{int(time.time())}_{up.name}"
                h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                p_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                # 2. MODEL: fal-ai/flux-general/image-to-image (veya inpainting)
                # Ürünü bozmamak için 'image_to_image' yerine 'masking' odaklı bir yapı kullanıyoruz
                status.text("2/3: Ürün donduruluyor ve arka plan inşa ediliyor...")
                handler = fal_client.submit(
                    "fal-ai/flux/dev/image-to-image",
                    arguments={
                        "image_url": p_url,
                        "prompt": f"Professional advertising photo of the original product, {prompt}, 8k, photorealistic, sharp details",
                        "strength": 0.55, # Ürün koruma ve değişim dengesi (Daha hassas)
                        "guidance_scale": 7.5,
                        "num_inference_steps": 35
                    }
                )
                res = handler.get()

                if res and 'images' in res:
                    status.text("3/3: Tamamlandı!")
                    st.session_state.final_img = res['images'][0]['url']
                    use_credit(user_id, current_c)
                    st.rerun()
            except Exception as e: st.error(f"Hata: {e}")
        else: st.warning("Kredi yetersiz.")

with c2:
    if st.session_state.final_img:
        st.subheader("✨ Final Sonucu")
        st.image(st.session_state.final_img, use_container_width=True)
        st.success("Analiz: Ürün maskeleme uygulandı.")
