import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="SnapBackground AI v2.0", layout="wide")

# FAL_KEY Konfigürasyonu
FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
os.environ["FAL_KEY"] = FAL_KEY

SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"

# --- SIDEBAR (TASARIM AYARLARI) ---
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
    
    # Fooocus modelinde 'image_prompt_strength' ürünün korunma seviyesini belirler
    koruma_seviyesi = st.slider("Ürün Koruma Oranı (Yüksek = Daha Az Değişim)", 0.5, 1.0, 0.75)

# --- ANA EKRAN ---
st.title("📸 SnapBackground AI - Profesyonel Reklam Stüdyosu")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🖼️ Orijinal Fotoğraf")
    uploaded_file = st.file_uploader("Ürünü buraya sürükleyin...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
        default_prompt = sablon_promptlar.get(sablon, "professional advertising photography")
        user_prompt = st.text_area("Tarif edin (İngilizce):", default_prompt)

with col2:
    st.subheader("✨ AI Çıktısı")
    if uploaded_file and st.button("Sihri Başlat 🚀"):
        with st.spinner('Yapay zeka ürününüzü işliyor...'):
            try:
                # 1. SUPABASE ÜZERİNE GEÇİCİ YÜKLEME
                file_name = f"{int(time.time())}_{uploaded_file.name}"
                upload_url = f"{SUPABASE_URL}/storage/v1/object/photos/{file_name}"
                headers = {
                    "Authorization": f"Bearer {SUPABASE_KEY}", 
                    "apikey": SUPABASE_KEY, 
                    "Content-Type": uploaded_file.type
                }
                
                # Dosyayı buluta yükle
                requests.post(upload_url, data=uploaded_file.getvalue(), headers=headers)
                image_public_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{file_name}"

                # 2. FAL.AI FOOOCUS MODELİNİ ÇALIŞTIR (ÜRÜN KORUMA MODU)
                handler = fal_client.submit(
                    "fal-ai/fooocus/image-prompt",
                    arguments={
                        "prompt": f"Professional product photography, {user_prompt}, highly detailed, 8k",
                        "image_url": image_public_url,
                        "input_image_url": image_public_url,
                        "image_prompt_strength": koruma_seviyesi,
                        "image_prompt_model": "face_swap", # Ürün hatlarını donduran mod
                        "negative_prompt": "mutated, deformed, blurry, low quality, distorted, missing parts, unrecognizable product, messy",
                        "guidance_scale": 4
                    }
                )
                
                result = handler.get()
                
                if result and 'images' in result:
                    resim_url = result['images'][0]['url']
                    st.image(resim_url, use_container_width=True)
                    
                    # İndirme Butonu
                    response = requests.get(resim_url)
                    st.download_button("📷 Fotoğrafı İndir", data=response.content, file_name="snap_background_result.png")
                    st.balloons()
                else:
                    st.warning("Yapay zeka bir sonuç döndüremedi. Lütfen tekrar deneyin.")

            except Exception as e:
                st.error(f"Hata oluştu: {e}")
