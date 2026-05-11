import streamlit as st
import base64
from openai import OpenAI
from supabase import create_client

# --- AYARLAR VE BAĞLANTILAR ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- KULLANICI BİLGİLERİNİ ÇEKME ---
def get_user_data(email):
    res = supabase.table("profiller").select("*").eq("e-posta", email).single().execute()
    return res.data

def update_kredi(user_id, yeni_kredi):
    supabase.table("profiller").update({"krediler": yeni_kredi}).eq("id", user_id).execute()

# --- ANA UYGULAMA ---
def main():
    # Hafızayı ilklendirme (Sonuçların kaybolmaması için)
    if "seo_result" not in st.session_state:
        st.session_state.seo_result = None

    user_data = get_user_data("furkangunay733@gmail.com")
    current_kredi = user_data['krediler']

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("💎 PRO Satıcı")
        st.metric("Kalan Kredi", current_kredi)
        
        st.markdown("---")
        st.subheader("Kredi Yükle")
        checkout_url = "https://getsnapbackground.lemonsqueezy.com/checkout/buy/a35adaa5-735c-4ffb-936d-442576c4c753"
        st.markdown(f'''
            <a href="{checkout_url}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #FF4B4B; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold;">
                    🔥 100 Kredi Satın Al
                </div>
            </a>
        ''', unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Güvenli Çıkış"):
            st.session_state.logged_in = False
            st.rerun()

    # --- ANA PANEL ---
    st.title("🚀 Etsy SEO & Tanım Uzmanı")
    st.info("Ürün fotoğrafınızı yükleyin, AI sizin için satış arttıran SEO ayarlarını yapsın.")

    uploaded_file = st.file_uploader("Ürün Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])
    lang = st.selectbox("Çıktı Dili", ["English", "Turkish", "German", "French"])

    if st.button("SEO Analizini Başlat ✨"):
        if not uploaded_file:
            st.warning("Lütfen önce bir fotoğraf yükleyin!")
        elif current_kredi <= 0:
            st.error("Krediniz tükenmiş! Lütfen yan menüden kredi yükleyin.")
        else:
            with st.spinner("AI fotoğrafı inceliyor ve strateji oluşturuyor..."):
                try:
                    base64_image = image_to_base64(uploaded_file)
                    
                    prompt_text = f"""
                    You are an Etsy SEO expert. Analyze the product in this image and provide the following in {lang}:
                    
                    1. **Title**: A high-converting title (max 140 chars).
                    2. **SEO Tags**: 13 powerful tags separated by commas.
                    3. **Description**: A short, engaging product description focusing on benefits.
                    
                    Please provide the results directly starting with the Title.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_text},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ],
                            }
                        ],
                        max_tokens=500,
                    )

                    # Sonucu hafızaya al
                    st.session_state.seo_result = response.choices[0].message.content
                    
                    # Krediyi düşür
                    yeni_kredi = current_kredi - 1
                    update_kredi(user_data['id'], yeni_kredi)
                    
                    # Sayfayı yenile (Kredi bilgisinin güncellenmesi için)
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")

    # --- SONUÇLARI GÖSTERME (Hafızadan çeker) ---
    if st.session_state.seo_result:
        st.success("Analiz Başarıyla Tamamlandı!")
        st.markdown("### 📝 GPT-4o SEO Analizi")
        st.text_area("Kopyalamaya Hazır Veri", value=st.session_state.seo_result, height=400)
        
        # Yeni bir analiz için temizleme butonu (Opsiyonel)
        if st.button("Sonuçları Temizle"):
            st.session_state.seo_result = None
            st.rerun()

if __name__ == "__main__":
    main()
