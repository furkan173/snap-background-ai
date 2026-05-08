import streamlit as st
import fal_client
import requests
import time

# --- AYARLAR ---
st.set_page_config(page_title="AI Reklam Stüdyosu v2.0 (Fal.ai)", layout="wide")

# FAL_KEY Buraya (Tırnak içine resimdeki 6b61... ile başlayan tam kodu yapıştır)
FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
import os
os.environ["FAL_KEY"] = FAL_KEY

SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Tasarım Ayarları")
    sablon = st.selectbox(
        "Arka Plan Teması Seçin:",
        ["Özel", "Lüks Mermer Masa", "Modern Ofis", "Yaz Bahçesi", "Stüdyo Karanlık Mod"]
    )
    
    sablon_promptlar = {
        "Lüks Mermer Masa": "on a luxury white marble table, elegant shadows, high-end product photography",
        "Modern Ofis": "on a clean wooden office desk, professional workspace, soft daylight",
        "Yaz Bahçesi": "outdoors in a sunny garden, natural green background, warm sunlight",
        "Stüdyo Karanlık Mod": "dark studio background, dramatic rim lighting, cinematic shadows"
    }
    yaraticilik = st.slider("Değişim Oranı", 0.0, 1.0, 0.6)

# --- ANA EKRAN ---
st.title("📸 AI Profesyonel Reklam Stüdyosu")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🖼️ Orijinal Fotoğraf")
    uploaded_file = st.file_uploader("Ürünü buraya sürükleyin...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
        user_prompt = st.text_area("Tarif edin:", sablon_promptlar.get(sablon, "professional advertising photography"))

with col2:
    st.subheader("✨ AI Çıktısı")
    if uploaded_file and st.button("Sihri Başlat 🚀"):
        with st.spinner('Fal.ai saniyeler içinde hazırlıyor...'):
            try:
                # 1. SUPABASE YÜKLEME
                file_name = f"{int(time.time())}_{uploaded_file.name}"
                upload_url = f"{SUPABASE_URL}/storage/v1/object/photos/{file_name}"
                headers = {"Authorization": f"Bearer {SUPABASE_KEY}", "apikey": SUPABASE_KEY, "Content-Type": uploaded_file.type}
                requests.post(upload_url, data=uploaded_file.getvalue(), headers=headers)
                image_public_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{file_name}"

                # 2. FAL.AI ÇALIŞTIR (SDXL Image-to-Image)
                handler = fal_client.submit(
                    "fal-ai/fast-sdxl/image-to-image",
                    arguments={
                        "image_url": image_public_url,
                        "prompt": f"Product photography, {user_prompt}, highly detailed, 8k",
                        "strength": yaraticilik
                    }
                )
                
                result = handler.get()
                if result and 'images' in result:
                    resim_url = result['images'][0]['url']
                    st.image(resim_url, use_container_width=True)
                    
                    response = requests.get(resim_url)
                    st.download_button("📷 Fotoğrafı İndir", data=response.content, file_name="ai_reklam.png")
                    st.balloons()

            except Exception as e:
                st.error(f"Hata oluştu: {e}")