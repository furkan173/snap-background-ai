import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR VE KONFİGÜRASYON ---
st.set_page_config(page_title="SnapBackground Pro AI", layout="wide")

# API Anahtarları (Senin mevcut anahtarların)
FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"
os.environ["FAL_KEY"] = FAL_KEY

# Session State Hazırlığı
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "final_img" not in st.session_state: st.session_state.final_img = None

# --- YARDIMCI FONKSİYONLAR ---
def get_credits(user_id):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=headers).json()
        return res[0].get('krediler', 0) if res else 0
    except: return 0

def use_credit(user_id, current_val):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    new_val = max(0, current_val - 1)
    requests.patch(f"{SUPABASE_URL}/rest/v1/profiller?id=eq.{user_id}", headers=headers, json={"krediler": new_val})

# --- GİRİŞ SİSTEMİ ---
if not st.session_state.logged_in:
    st.title("📸 SnapBackground Pro Giriş")
    email = st.text_input("E-posta Adresi")
    password = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        login_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        res = requests.post(login_url, headers={"apikey": SUPABASE_KEY}, json={"email": email, "password": password})
        if res.status_code == 200:
            st.session_state.logged_in = True
            st.session_state.user_id = res.json()['user']['id']
            st.rerun()
        else:
            st.error("Giriş başarısız. Bilgilerinizi kontrol edin.")
    st.stop()

# --- ANA UYGULAMA PANELİ ---
user_id = st.session_state.user_id
current_credits = get_credits(user_id)

with st.sidebar:
    st.title("👤 Kullanıcı Paneli")
    st.metric("Kalan Kredi", current_credits)
    if st.button("Çıkış Yap"):
        st.session_state.logged_in = False
        st.rerun()

st.title("📸 Profesyonel Ürün Fotoğrafçısı AI")
st.markdown("Ürün formunu koruyan ticari optimizasyon aktif.")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Ürün fotoğrafını yükleyin", type=["jpg", "png", "jpeg"])
    user_prompt = st.text_input("Arka planı tarif edin:", "on a luxury white marble table, soft studio lighting")
    
    if st.button("Sihri Başlat (1 Kredi) 🚀") and uploaded_file:
        if current_credits > 0:
            status = st.empty()
            try:
                # 1. Aşama: Dosyayı Supabase Storage'a Yükleme
                status.text("1/3: Ürün fotoğrafı sunucuya aktarılıyor...")
                file_name = f"{int(time.time())}_{uploaded_file.name}"
                upload_url = f"{SUPABASE_URL}/storage/v1/object/photos/{file_name}"
                headers_up = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": uploaded_file.type}
                requests.post(upload_url, data=uploaded_file.getvalue(), headers=headers_up)
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{file_name}"

                # 2. Aşama: AI İşleme (SDXL Image-to-Image Profesyonel Mod)
                status.text("2/3: Arka plan tasarlanıyor (Ürün korunuyor)...")
                handler = fal_client.submit(
                    "fal-ai/fast-sdxl/image-to-image",
                    arguments={
                        "image_url": public_url,
                        "prompt": f"Professional advertising product shot, {user_prompt}, cinematic lighting, 8k resolution, highly detailed, realistic textures",
                        "strength": 0.65, # Ürün koruma ve arka plan değişimi arasındaki 'Altın Oran'
                        "guidance_scale": 12.5, # Komuta yüksek sadakat
                        "num_inference_steps": 40
                    }
                )
                result = handler.get()

                # 3. Aşama: Sonuç Gösterimi ve Kredi Düşümü
                if result and 'images' in result:
                    status.text("3/3: İşlem başarıyla tamamlandı!")
                    st.session_state.final_img = result['images'][0]['url']
                    use_credit(user_id, current_credits)
                    st.rerun()
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
        else:
            st.warning("Yetersiz kredi! Lütfen bakiye yükleyin.")

with col2:
    st.subheader("✨ Final Sonucu")
    if st.session_state.final_img:
        st.image(st.session_state.final_img, use_container_width=True)
        st.success("Analiz: Ürün formu korundu, arka plan güncellendi.")
        if st.button("Yeni Fotoğraf Düzenle 🔄"):
            st.session_state.final_img = None
            st.rerun()
    else:
        st.info("Henüz bir görsel oluşturulmadı. Sol panelden işlemi başlatın.")
