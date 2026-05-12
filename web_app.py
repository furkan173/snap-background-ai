import streamlit as st
import base64
from openai import OpenAI
from supabase import create_client

# --- CONFIGURATION ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
USER_EMAIL = "furkangunay733@gmail.com"

# --- HELPER FUNCTIONS ---
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def get_user_data(email):
    res = supabase.table("profiller").select("*").eq("e-posta", email).single().execute()
    return res.data

def update_kredi(user_id, yeni_kredi):
    supabase.table("profiller").update({"krediler": yeni_kredi}).eq("id", user_id).execute()

def save_to_history(email, tip, girdi, sonuc):
    try:
        supabase.table("analiz_gecmisi").insert({
            "user_email": str(email),
            "analiz_tipi": str(tip),
            "girdi_verisi": str(girdi),
            "sonuc_metni": str(sonuc)
        }).execute()
    except Exception as e:
        st.error(f"History Save Error: {e}")

# --- LANDING PAGE ---
def render_landing_page():
    # Logo ve Başlık
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.image("etsy.jpg", width=200)
    
    st.markdown("""
        <div style="text-align: center; padding: 20px 0px;">
            <h1 style="font-size: 3.2rem; color: #FF4B4B;">Skyrocket Your Etsy Sales</h1>
            <p style="font-size: 1.4rem; color: #555;">The All-in-One AI Marketing Suite for Professional Sellers.</p>
        </div>
    """, unsafe_allow_html=True)

    # Özellikler Paneli
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### ✨ AI SEO")
        st.write("Generate high-converting titles, tags, and descriptions using GPT-4o.")
    with col2:
        st.markdown("### 🔍 Competitor Spy")
        st.write("Analyze competitor listings and find their strategic weaknesses.")
    with col3:
        st.markdown("### 📊 Health Score")
        st.write("Get instant AI feedback on your listing's SEO health and tips.")

    st.markdown("---")
    
    # Giriş Butonu
    if st.button("🚀 Get Started / Open Dashboard", use_container_width=True, type="primary"):
        st.session_state.show_app = True
        st.rerun()

# --- MAIN APP ---
def main():
    # Sayfa durumu kontrolü
    if 'show_app' not in st.session_state:
        st.session_state.show_app = False

    if not st.session_state.show_app:
        render_landing_page()
    else:
        # ASIL UYGULAMA PANELİ
        try:
            user_data = get_user_data(USER_EMAIL)
            current_kredi = user_data['krediler']
        except Exception as e:
            st.error(f"Profile connection error: {e}")
            return

        # --- SIDEBAR ---
        with st.sidebar:
            st.image("etsy.jpg", width=150)
            st.title("💎 EtsyFocus PRO")
            st.metric("Credits Remaining", current_kredi)
            st.markdown("---")
            st.subheader("Upgrade")
            checkout_url = "https://getsnapbackground.lemonsqueezy.com/checkout/buy/a35adaa5-735c-4ffb-936d-442576c4c753"
            st.markdown(f'<a href="{checkout_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#FF4B4B;color:white;padding:12px;border-radius:8px;text-align:center;font-weight:bold;">🔥 Get 100 Credits</div></a>', unsafe_allow_html=True)
            if st.button("Logout"):
                st.session_state.show_app = False
                st.rerun()

        st.title("🚀 Global Etsy Marketing Suite")
        
        tab1, tab2, tab3, tab4 = st.tabs(["✨ SEO Generator", "🔍 Competitor Analysis", "📊 Listing Score", "📜 History"])

        # --- TAB 1: SEO GENERATOR ---
        with tab1:
            st.header("AI SEO Optimizer")
            uploaded_file = st.file_uploader("Upload Product Photo", type=["jpg", "png"], key="seo_up")
            lang = st.selectbox("Language", ["English", "German", "French", "Turkish"], key="seo_lang")
            
            if st.button("Generate Strategy ✨"):
                if uploaded_file and current_kredi > 0:
                    with st.spinner("Analyzing image..."):
                        base64_img = image_to_base64(uploaded_file)
                        prompt = f"Analyze this product for Etsy. Provide Title, 13 Tags, and Description in {lang}."
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}],
                        )
                        res_text = response.choices[0].message.content
                        st.write(res_text)
                        
                        save_to_history(USER_EMAIL, "SEO Generator", uploaded_file.name, res_text)
                        update_kredi(user_data['id'], current_kredi - 1)
                        st.balloons()
                else:
                    st.warning("Please upload a photo or check credits.")

        # --- TAB 2: COMPETITOR ANALYSIS ---
        with tab2:
            st.header("Spy on Competitors")
            comp_file = st.file_uploader("Upload Competitor Image", type=["jpg", "png"], key="comp_up")
            
            if st.button("Analyze Competitor 🔍"):
                if comp_file and current_kredi > 0:
                    with st.spinner("Decoding competitor..."):
                        base64_img = image_to_base64(comp_file)
                        prompt = "Analyze this competitor's product. Identify keywords, weaknesses, and suggest how I can outperform them."
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}],
                        )
                        res_text = response.choices[0].message.content
                        st.markdown("### 🏆 Strategic Insights")
                        st.write(res_text)
                        
                        save_to_history(USER_EMAIL, "Competitor Analysis", comp_file.name, res_text)
                        update_kredi(user_data['id'], current_kredi - 1)
                else:
                    st.warning("Check image or credits.")

        # --- TAB 3: LISTING SCORE ---
        with tab3:
            st.header("Listing Health Check")
            u_title = st.text_input("Current Title")
            u_tags = st.text_area("Current Tags")
            
            if st.button("Get Score 📊"):
                if u_title and current_kredi > 0:
                    with st.spinner("Auditing..."):
                        prompt = f"Rate this Etsy SEO out of 100. Title: {u_title}, Tags: {u_tags}."
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "user", "content": prompt}],
                        )
                        res_text = response.choices[0].message.content
                        st.write(res_text)
                        
                        save_to_history(USER_EMAIL, "Listing Score", u_title[:30], res_text)
                        update_kredi(user_data['id'], current_kredi - 1)
                else:
                    st.warning("Fill title and check credits.")

        # --- TAB 4: HISTORY ---
        with tab4:
            st.header("Your Recent Activity")
            try:
                history_res = supabase.table("analiz_gecmisi").select("*").eq("user_email", USER_EMAIL).order("olusturma_tarihi", desc=True).limit(15).execute()
                if history_res.data:
                    for item in history_res.data:
                        tarih = item['olusturma_tarihi'][:16].replace("T", " ")
                        with st.expander(f"🕒 {tarih} - {item['analiz_tipi']}"):
                            st.info(f"**Input:** {item['girdi_verisi']}")
                            st.write(item['sonuc_metni'])
                else:
                    st.info("No records found.")
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
