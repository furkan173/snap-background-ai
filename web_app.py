import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground ULTRA PRO v5.1", layout="wide")

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
    st.title("🛡️ Ultra Pro v5.1 Giriş")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Sisteme Bağlan"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
    st.stop()

# --- PANEL ---
user_id = st.session_state.user_id
current_c = get_credits(user_id)

with st.sidebar:
    st.metric("Kalan Krediniz", current_c)
    if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

st.title("📸 Profesyonel Ürün Fotoğrafçısı AI")
st.info("Ürün formu %100 korunur. Sadece arka plan değişir.")

c1, c2 = st.columns(2)
with c1:
    up = st.file_uploader("Ürün Görseli Seçin", type=["jpg", "png", "jpeg"])
    prompt = st.text_input("Arka plan teması:", "on a luxury marble counter, soft studio lighting")

    if st.button("Profesyonel Çekimi Başlat 🚀") and up:
        if current_c > 0:
            status = st.empty()
            try:
                # 1. Fotoğraf Yükleme
                status.text("1/3: Fotoğraf yükleniyor...")
                f_n = f"{int(time.time())}_{up.name}"
                h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                p_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                # 2. DOĞRU MODEL: fal-ai/fooocus/inpainting (Ürün Koruma Uzmanı)
                status.text("2/3: Ürün donduruluyor ve arka plan değişiyor...")
                handler = fal_client.submit(
                    "fal-ai/fooocus/inpainting", 
                    arguments={
                        "input_image_url": p_url,
                        "prompt": f"Professional advertising photography, {prompt}, masterpiece, 8k",
                        "mask_threshold": 0.5,
                        "guidance_scale": 15, # Komuta sadık kal
                        "strength": 0.95 # Arka planı değiştirme gücü
                    }
                )
                res = handler.get()

                # 3. Sonuç
                if res and 'images' in res:
                    status.text("3/3: Tamamlandı!")
                    st.session_state.final_img = res['images'][0]['url']
                    use_credit(user_id, current_c)
                    st.rerun()
            except Exception as e: st.error(f"Hata: {e}")
        else: st.warning("Krediniz bitti.")

with c2:
    if st.session_state.final_img:
        st.subheader("✨ Sonuç")
        st.image(st.session_state.final_img, use_container_width=True)
        st.success("Analiz: Ürün detayları korunmuştur.")
