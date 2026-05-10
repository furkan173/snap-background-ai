import streamlit as st
import fal_client
import requests
import time
import os

# --- KONFİGÜRASYON ---
st.set_page_config(page_title="SnapBackground Pro AI", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"
os.environ["FAL_KEY"] = FAL_KEY

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "img_url" not in st.session_state: st.session_state.img_url = None

# --- VERİ FONKSİYONLARI ---
def get_credits(user_id):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    res = requests.get(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=headers).json()
    return res[0].get('krediler', 0) if res else 0

def decrease_credit(user_id, current):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    requests.patch(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=headers, json={"krediler": max(0, current - 1)})

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.title("🚀 SnapBackground Pro Giriş")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id, st.session_state.user_email = True, res.json()['user']['id'], e
            st.rerun()
    st.stop()

# --- ANA PANEL ---
credits = get_credits(st.session_state.user_id)
with st.sidebar:
    st.metric("Mevcut Krediniz", credits)
    if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

st.title("📸 Profesyonel Ürün Fotoğrafçısı AI")
st.info("Bu model ürün formunu korur ve profesyonel reklam ışığı ekler.")

c1, c2 = st.columns(2)
with c1:
    up = st.file_uploader("Ürün Fotoğrafı (Net ve Aydınlık olmalı)", type=["jpg", "png", "jpeg"])
    prompt = st.text_input("Arka Plan Teması:", "on a luxury white marble table, soft studio lighting, bokeh background")
    
    if st.button("Profesyonel Çekimi Başlat 🚀") and up:
        if credits > 0:
            with st.spinner("Ürün korunuyor ve sahne oluşturuluyor..."):
                try:
                    # 1. Fotoğraf Yükleme
                    f_name = f"{int(time.time())}_{up.name}"
                    headers_up = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                    requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_name}", data=up.getvalue(), headers=headers_up)
                    p_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_name}"

                    # 2. PRO MODEL: Fal.ai Image-to-Image (Product Focus)
                    # Bu ayar ürünü bir 'image prompt' olarak değil, ana yapı olarak görür
                    handler = fal_client.submit(
                        "fal-ai/fooocus/image-prompt",
                        arguments={
                            "prompt": f"Professional advertising shot of the product, {prompt}, masterpiece, 8k, extremely detailed, realistic textures",
                            "image_prompt_1": {"image_url": p_url},
                            "image_prompt_model_1": "image_prompt", 
                            "image_prompt_strength": 0.98, # Maksimum koruma
                            "guidance_scale": 12, # Komuta sadık kal
                            "sharpness": 2
                        }
                    )
                    res = handler.get()
                    if res and 'images' in res:
                        st.session_state.img_url = res['images'][0]['url']
                        decrease_credit(st.session_state.user_id, credits)
                        st.rerun()
                except Exception as ex: st.error(f"Hata: {ex}")
        else: st.warning("Kredi yükleyiniz.")

with c2:
    if st.session_state.img_url:
        st.image(st.session_state.img_url, caption="Profesyonel Sonuç", use_container_width=True)
        st.success("Ürün formu korundu. Satışa hazır!")
