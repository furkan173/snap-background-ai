import streamlit as st
import base64
from openai import OpenAI
from supabase import create_client

# --- CONFIGURATION ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
USER_EMAIL = "furkangunay733@gmail.com"

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

# --- MAIN APP ---
def main():
    try:
        user_data = get_user_data(USER_EMAIL)
        current_kredi = user_data['krediler']
    except Exception as e:
        st.error(f"Profile connection error: {e}")
        return

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("💎 EtsyFocus PRO")
        st.metric("Credits Remaining", current_kredi)
        st.markdown("---")
        st.subheader("Upgrade")
        checkout_url = "https://getsnapbackground.lemonsqueezy.com/checkout/buy/a35adaa5-735c-4ffb-936d-442576c4c753"
        st.markdown(f'<a href="{checkout_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#FF4B4B;color:white;padding:12px;border-radius:8px;text-align:center;font-weight:bold;">🔥 Get 100 Credits</div></a>', unsafe_allow_html=True)

    # --- MAIN INTERFACE ---
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
                st.warning("Please upload a photo or check your credits.")

    # --- TAB 2: COMPETITOR ANALYSIS ---
    with tab2:
        st.header("Spy on Competitors")
        st.info("Upload a screenshot of a competitor's listing to see how to beat them.")
        comp_file = st.file_uploader("Upload Competitor Image", type=["jpg", "png"], key="comp_up")
        
        if st.button("Analyze Competitor 🔍"):
            if comp_file and current_kredi > 0:
                with st.spinner("Decoding competitor strategy..."):
                    base64_img = image_to_base64(comp_file)
                    prompt = "Analyze this competitor's product. Identify keywords, weaknesses, and suggest how I can outperform them."
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}],
                    )
                    res_text = response.choices[0].message.content
                    st.markdown("### 🏆 How to Beat This Competitor")
                    st.write(res_text)
                    
                    save_to_history(USER_EMAIL, "Competitor Analysis", comp_file.name, res_text)
                    update_kredi(user_data['id'], current_kredi - 1)
            else:
                st.warning("Please upload an image or check credits.")

    # --- TAB 3: LISTING SCORE ---
    with tab3:
        st.header("Listing Health Check")
        user_title = st.text_input("Current Title")
        user_tags = st.text_area("Current Tags (comma separated)")
        
        if st.button("Get Score 📊"):
            if user_title and current_kredi > 0:
                with st.spinner("Auditing your SEO..."):
                    prompt = f"Rate this Etsy Listing SEO out of 100. Title: {user_title}, Tags: {user_tags}. Provide a Score and 3 actionable tips."
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "You are an Etsy SEO auditor."}, {"role": "user", "content": prompt}],
                    )
                    res_text = response.choices[0].message.content
                    st.write(res_text)
                    
                    save_to_history(USER_EMAIL, "Listing Score", user_title[:30], res_text)
                    update_kredi(user_data['id'], current_kredi - 1)
            else:
                st.warning("Title field is required!")

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
                st.info("No history records found.")
        except Exception as e:
            st.error(f"Error loading history: {e}")

if __name__ == "__main__":
    main()
