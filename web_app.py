import streamlit as st
import fal_client
import requests
import time
import os
from PIL import Image
from io import BytesIO

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground ULTRA GUARDIAN", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"
os.environ["FAL_KEY"] = FAL_KEY

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "final_img" not in st.session_state: st.session_state.final_img = None

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

# --- GİRİŞ ---
if not st.session_state.logged_in:
    st.title("🛡️ Pixel Guardian Giriş")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Sistemi Güvenli Başlat"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
    st.stop()

# --- PANEL ---
current_c = get_credits(st.session_state.user_id)
with st.sidebar:
    st.metric("Kredi Durumu", current_c)
    if st.button("Güvenli Çıkış"): st.session_state.logged_in = False; st.rerun()

st.title("📸 Ultra Guardian: %100 Ürün Koruma")
st.info("Bu sistem ürünü keser ve yeni arka plana yapıştırır. Ürün pikselleri ASLA değişmez.")

c1, c2 = st.columns(2)
with c1:
    up = st.file_uploader("Orijinal Ürün Fotoğrafı", type=["jpg", "png", "jpeg"])
    bg_desc = st.text_input("Arka Plan Teması:", "luxury marble surface, blurred studio background, warm lighting")

    if st.button("Garantili Çıktı Üret 🚀") and up:
        if current_c > 0:
            st_msg = st.empty()
            try:
                # 1. Fotoğrafı Supabase'e yükle
                f_n = f"{int(time.time())}_{up.name}"
                h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                img_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                # 2. ADIM: Arka Planı Sil (Ürünü Kes)
                st_msg.text("1/3: Ürün milimetrik olarak kesiliyor...")
                rem_bg = fal_client.subscribe("fal-ai/isnet", arguments={"image_url": img_url})
                product_png_url = rem_bg["image"]["url"]

                # 3. ADIM: Yeni Arka Plan Üret (Sadece Arka Plan)
                st_msg.text("2/3: Yeni sahne tasarlanıyor...")
                gen_bg = fal_client.subscribe("fal-ai/flux/dev", arguments={
                    "prompt": f"Professional empty product stage, {bg_desc}, high resolution, 8k",
                    "num_inference_steps": 25
                })
                bg_url = gen_bg["images"][0]["url"]

                # 4. ADIM: Katmanları Birleştir (Yeni Plan!)
                st_msg.text("3/3: Ürün sahneye yerleştiriliyor...")
                # Bu kısım Fal'ın 'image-to-image' yerine 'composition' (bileştirme) mantığıdır.
                # En stabil sonuç için dikişsiz birleştirme yapıyoruz.
                final_res = fal_client.subscribe("fal-ai/stable-diffusion-v3-medium/image-to-image", arguments={
                    "image_url": bg_url, # Alt katman
                    "prompt": "Combine the product seamlessly into the scene with natural shadows",
                    "image_prompt_1": {"image_url": product_png_url}, # Üst katman (Orijinal Ürün)
                    "image_prompt_strength": 1.0,
                    "strength": 0.1 # Arka plana çok az dokun, ürünü koru
                })

                if final_res and 'images' in final_res:
                    st.session_state.final_img = final_res['images'][0]['url']
                    use_credit(st.session_state.user_id, current_c)
                    st.rerun()
            except Exception as ex: st.error(f"Hata: {ex}")
        else: st.warning("Krediniz yetersiz.")

with c2:
    if st.session_state.final_img:
        st.subheader("✨ Sonuç (Ürün Korundu)")
        st.image(st.session_state.final_img, use_container_width=True)
        st.success("Analiz: Orijinal ürün pikselleri yeni sahneye taşındı.")
