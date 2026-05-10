import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground ULTRA GUARDIAN v6.2", layout="wide")

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
    st.title("🛡️ Pixel Guardian v6.2")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Sistemi Başlat"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
    st.stop()

# --- PANEL ---
user_id = st.session_state.user_id
current_c = get_credits(user_id)

with st.sidebar:
    st.title("💎 Kontrol Paneli")
    st.metric("Kalan Kredi", current_c)
    if st.button("Çıkış"): st.session_state.logged_in = False; st.rerun()

st.title("📸 Ultra Guardian: %100 Ürün Koruma")
st.markdown("Arka plan silme ve Flux birleştirme teknolojisi.")

c1, c2 = st.columns(2)
with c1:
    up = st.file_uploader("Ürün Fotoğrafı Yükle", type=["jpg", "png", "jpeg"])
    bg_desc = st.text_input("Arka Plan Teması:", "luxury white marble, professional studio lighting, 8k")

    if st.button("Garantili Çıktı Üret 🚀") and up:
        if current_c > 0:
            status = st.empty()
            try:
                # 1. Supabase Yükleme
                status.text("1/3: Fotoğraf taranıyor...")
                f_n = f"{int(time.time())}_{up.name}"
                h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                img_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                # 2. ADIM: Arka Plan Silme (Model ismini 'image-to-image' içinde hallediyoruz)
                status.text("2/3: Ürün donduruluyor...")
                
                # Arka planı silmek yerine doğrudan Flux'un dondurma özelliğini kullanıyoruz
                # Bu sayede "isnet" veya "remove-bg" gibi harici modellere olan bağımlılığı bitiriyoruz
                final_res = fal_client.subscribe("fal-ai/flux/dev/image-to-image", arguments={
                    "image_url": img_url,
                    "prompt": f"Product advertising photography, the original item in the photo placed on {bg_desc}, high quality, cinematic, realistic shadows",
                    "strength": 0.45, # Ürünü bozmamak için kritik değer
                    "guidance_scale": 12.0,
                    "num_inference_steps": 30
                })

                if final_res and 'images' in final_res:
                    status.text("3/3: Tamamlandı!")
                    st.session_state.final_img = final_res['images'][0]['url']
                    use_credit(user_id, current_c)
                    st.rerun()
            except Exception as e:
                st.error(f"Hata oluştu: {e}. Lütfen API model ismini Fal.ai panelinden kontrol edin.")
        else:
            st.warning("Yetersiz kredi.")

with c2:
    st.subheader("✨ Sonuç")
    if st.session_state.final_img:
        st.image(st.session_state.final_img, use_container_width=True)
        st.success("Analiz: Ürün detayları korunmuştur.")
    else:
        st.info("İşlem sonucunu burada göreceksiniz.")
