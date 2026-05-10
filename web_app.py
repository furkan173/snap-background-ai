import streamlit as st
import fal_client
import requests
import time
import os
from streamlit_supabase_auth import login_form, logout_button

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground AI v3.0", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
os.environ["FAL_KEY"] = FAL_KEY

SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"

# --- GİRİŞ SİSTEMİ (AUTH) ---
session = login_form(url=SUPABASE_URL, apiKey=SUPABASE_KEY)

if not session:
    st.info("Lütfen devam etmek için giriş yapın veya kayıt olun.")
    st.stop()

# Giriş yapan kullanıcının bilgileri
user_id = session['user']['id']
user_email = session['user']['email']

# --- VERİTABANI FONKSİYONLARI ---
def get_user_credits():
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY}
    response = requests.get(f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=credits", headers=headers)
    data = response.json()
    if data:
        return data[0]['credits']
    else:
        # Eğer profil yoksa oluştur (5 kredi ile)
        requests.post(f"{SUPABASE_URL}/rest/v1/profiles", 
                      headers=headers, 
                      json={"id": user_id, "email": user_email, "credits": 5})
        return 5

def decrease_credit(current_credits):
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    new_credits = current_credits - 1
    requests.patch(f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}", 
                   headers=headers, 
                   json={"credits": new_credits})
    return new_credits

# --- SIDEBAR ---
with st.sidebar:
    st.title("👤 Profilim")
    st.write(f"Merhaba, **{user_email}**")
    
    current_credits = get_user_credits()
    st.metric("Kalan Kredi", current_credits)
    
    st.divider()
    logout_button()
    
    st.title("⚙️ Tasarım Ayarları")
    sablon = st.selectbox("Arka Plan Teması:", ["Özel", "Lüks Mermer Masa", "Modern Ofis", "Yaz Bahçesi", "Stüdyo Karanlık Mod"])
    koruma_seviyesi = st.slider("Ürün Koruma Oranı", 0.5, 1.0, 0.85)

# --- ANA EKRAN ---
st.title("📸 SnapBackground AI - Profesyonel Stüdyo")

if current_credits <= 0:
    st.error("❌ Krediniz bitmiştir. Lütfen paket satın alın.")
else:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🖼️ Orijinal Fotoğraf")
        uploaded_file = st.file_uploader("Ürünü sürükleyin...", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
            user_prompt = st.text_area("Tarif edin (İngilizce):", "professional advertising photography")

    with col2:
        st.subheader("✨ AI Çıktısı")
        if uploaded_file and st.button("Sihri Başlat (1 Kredi) 🚀"):
            with st.spinner('Yapay zeka işliyor...'):
                try:
                    # 1. Fotoğrafı Supabase'e Yükle
                    file_name = f"{int(time.time())}_{uploaded_file.name}"
                    upload_url = f"{SUPABASE_URL}/storage/v1/object/photos/{file_name}"
                    headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": uploaded_file.type}
                    requests.post(upload_url, data=uploaded_file.getvalue(), headers=headers)
                    image_public_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{file_name}"

                    # 2. Fal.ai Fooocus Çalıştır
                    handler = fal_client.submit(
                        "fal-ai/fooocus/image-prompt",
                        arguments={
                            "prompt": f"Professional product photography, {user_prompt}, highly detailed, 8k",
                            "image_prompt_1": {"image_url": image_public_url},
                            "image_prompt_model_1": "face_swap",
                            "image_prompt_strength": koruma_seviyesi,
                            "negative_prompt": "mutated, deformed, blurry, low quality",
                            "guidance_scale": 4
                        }
                    )
                    result = handler.get()
                    
                    if result and 'images' in result:
                        resim_url = result['images'][0]['url']
                        st.image(resim_url, use_container_width=True)
                        
                        # 3. Krediyi Düşür
                        new_val = decrease_credit(current_credits)
                        st.success(f"Görsel oluşturuldu! Kalan krediniz: {new_val}")
                        st.balloons()
                    else:
                        st.error("Görsel oluşturulamadı.")
                except Exception as e:
                    st.error(f"Hata: {e}")
