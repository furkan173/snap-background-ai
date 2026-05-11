import streamlit as st
import fal_client
import requests
import time
import os

# --- AYARLAR ---
st.set_page_config(page_title="Etsy SEO Magic AI v1.2", layout="wide")

FAL_KEY = "6b6185ff-1f55-41a4-983e-c52708afe67e:3b1962c534d970270346435115182232"
SUPABASE_URL = "https://ndfavrrmyrmtdixzpome.supabase.co"
SUPABASE_KEY = "sb_secret_s4P2_-OJol1tGBcXi71IZA_vIp3oTpO"
os.environ["FAL_KEY"] = FAL_KEY

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "seo_output" not in st.session_state: st.session_state.seo_output = None

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

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.title("📦 Etsy SEO Magic AI")
    st.info("Lütfen mağaza sahibi girişi yapın.")
    e = st.text_input("E-posta")
    p = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        res = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=password", headers={"apikey": SUPABASE_KEY}, json={"email": e, "password": p})
        if res.status_code == 200:
            st.session_state.logged_in, st.session_state.user_id = True, res.json()['user']['id']
            st.rerun()
        else:
            st.error("Giriş başarısız. Bilgilerinizi kontrol edin.")
    st.stop()

# --- ANA PANEL ---
user_id = st.session_state.user_id
current_c = get_credits(user_id)

with st.sidebar:
    st.title("💎 Satıcı Hesabı")
    st.metric("Kalan Kredi", current_c)
    if st.button("Güvenli Çıkış"): 
        st.session_state.logged_in = False
        st.rerun()

st.title("🚀 Etsy SEO & Tanım Oluşturucu")
st.markdown("Ürün fotoğrafını yükle, AI senin için en iyi SEO başlığını ve etiketlerini hazırlasın.")

c1, c2 = st.columns([1, 1.5])

with c1:
    up = st.file_uploader("Ürün Fotoğrafını Buraya Bırakın", type=["jpg", "png", "jpeg"])
    lang = st.selectbox("Sonuç Dili", ["English", "Turkish"])
    
    if st.button("SEO Paketini Hazırla ✨") and up:
        if current_c > 0:
            with st.spinner("AI ürünü inceliyor ve anahtar kelimeleri seçiyor..."):
                try:
                    # 1. Dosyayı Supabase'e Yükle
                    f_n = f"{int(time.time())}_{up.name}"
                    h_u = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": up.type}
                    requests.post(f"{SUPABASE_URL}/storage/v1/object/photos/{f_n}", data=up.getvalue(), headers=h_u)
                    img_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{f_n}"

                    # 2. Moondream ile Vision Analizi
                    result = fal_client.subscribe("fal-ai/moondream/batched", arguments={
                        "inputs": [
                            {
                                "image_url": img_url,
                                "prompt": f"Act as an Etsy SEO Expert. Look at this product and provide: 1. A catchy high-ranking Etsy Title. 2. 13 comma-separated Tags. 3. A professional product description with features and benefits. Output Language: {lang}"
                            }
                        ]
                    })

                    if result and 'outputs' in result:
                        st.session_state.seo_output = result['outputs'][0]
                        use_credit(user_id, current_c)
                        st.rerun()
                    else:
                        st.error("Modelden yanıt alınamadı, lütfen tekrar deneyin.")

                except Exception as ex:
                    st.error(f"Sistem Hatası: {ex}")
        else:
            st.warning("İşlem için yeterli krediniz kalmadı.")

with c2:
    st.subheader("📝 Hazır SEO Verileri")
    if st.session_state.seo_output:
        st.text_area("Kopyalamaya Hazır:", st.session_state.seo_output, height=450)
        st.success("Tebrikler! Veriler Etsy algoritmasına uygun şekilde hazırlandı.")
        if st.button("Yeni Ürün Analiz Et 🔄"):
            st.session_state.seo_output = None
            st.rerun()
    else:
        st.info("Analiz sonuçları burada görünecek.")
