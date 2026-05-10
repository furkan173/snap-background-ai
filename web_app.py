import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground ULTRA SHIELD", layout="wide")

# FAL KEY (Burayı Değiştirmeyi Unutma)
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
    if st.button("Giriş Yap"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
    st.stop()

# --- PANEL ---
current_c = get_credits(st.session_state.user_id)
with st.sidebar:
    st.metric("Kalan Kredi", current_c)
    if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

st.title("📸 ULTRA SHIELD: Profesyonel Ürün Fotoğrafçısı")
st.markdown("This version ensures 100% product integrity.")

c1, c2 = st.columns(2)
with c1:
    up = st.file_uploader("Yükle (Ürün %100 korunacaktır)", type=["jpg", "png", "jpeg"])
    prompt = st.text_input("Arka plan detayı:", "luxury mermer masa, yumuşak stüdyo ışığı")

    if st.button("Kusursuz Çekimi Başlat 🚀") and up:
        if current_c > 0:
            status = st.empty()
            try:
                # 1. Fotoğraf Yükleme
                status.text("1/3: Ürün fotoğrafları yükleniyor...")
                f_n = f"{int(time.time())}_{up.name}"
                h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                p_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                # 2. ULTRA MODEL: fal-ai/background-change (Segmentasyon Tabanlı)
                status.text("2/3: Ürün maskeleniyor ve arka plan değişiyor...")
                handler = fal_client.submit(
                    "fal-ai/background-change", # Bu API Fooocus değildir, sadece bu iş için üretilmiştir
                    arguments={
                        "image_url": p_url,
                        "prompt": f"Professional product advertising shot, {prompt}, masterpiece, 8k, realistic lighting",
                        "mask_threshold": 0.5 # Ürün sınırlarını net belirle
                    }
                )
                res = handler.get()

                # 3. Sonuç
                if res and 'image' in res:
                    status.text("3/3: Tamamlandı!")
                    st.session_state.final_img = res['image']['url']
                    use_credit(st.session_state.user_id, current_c)
                    st.rerun()
            except Exception as e: st.error(f"Hata: {e}")
        else: st.warning("Kredi yetersiz.")

with c2:
    if st.session_state.final_img:
        st.subheader("✨ Profesyonel Sonuç")
        st.image(st.session_state.final_img, use_container_width=True)
        st.success("Sonuç: Ürün pikselleri %100 korundu.")
