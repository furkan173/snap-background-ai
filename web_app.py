import streamlit as st
import base64
from openai import OpenAI
from supabase import create_client

# --- CONFIGURATION ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def get_user_data(email):
    res = supabase.table("profiller").select("*").eq("e-posta", email).single().execute()
    return res.data

def update_kredi(user_id, yeni_kredi):
    supabase.table("profiller").update({"krediler": yeni_kredi}).eq("id", user_id).execute()

# --- MAIN APP ---
def main():
    try:
        user_data = get_user_data("furkangunay733@gmail.com")
        current_kredi = user_data['krediler']
    except:
        st.error("Profile connection error.")
        return

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("💎 EtsyFocus PRO")
        st.metric("Credits Remaining", current_kredi)
        st.markdown("---")
        st.subheader("Upgrade")
        checkout_url = "https://getsnapbackground.lemonsqueezy.com/checkout/buy/a35adaa5-735c-4ffb-936d-442576c4c753"
        st.markdown(f'<a href="{checkout_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#FF4B4B;color:white;padding:12px;border-radius:8px;text-align:center;font-weight:bold;">🔥 Get 100 Credits</div></a>', unsafe_allow_html=True)
        if st.button("Sign Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- MAIN INTERFACE WITH TABS ---
    st.title("🚀 Global Etsy Marketing Suite")
    
    tab1, tab2, tab3 = st.tabs(["✨ SEO Generator", "🔍 Competitor Analysis", "📊 Listing Score"])

    # --- TAB 1: SEO GENERATOR ---
    with tab1:
        st.header("AI SEO Optimizer")
        uploaded_file = st.file_uploader("Upload Product Photo", type=["jpg", "png"], key="seo_up")
        lang = st.selectbox("Language", ["English", "German", "French", "Turkish"], key="seo_lang")
        
        if st.button("Generate Strategy ✨"):
            if uploaded_file and current_kredi > 0:
                with st.spinner("Analyzing..."):
                    base64_img = image_to_base64(uploaded_file)
                    prompt = f"Analyze this product for Etsy. Provide Title, 13 Tags, and Description in {lang}."
                    # API Call logic (existing)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}],
                    )
                    st.write(response.choices[0].message.content)
                    update_kredi(user_data['id'], current_kredi - 1)
                    st.balloons()
            else:
                st.warning("Check photo or credits!")

    # --- TAB 2: COMPETITOR ANALYSIS ---
    with tab2:
        st.header("Spy on Competitors")
        st.info("Upload a screenshot of a competitor's listing or their product photo to see how to beat them.")
        comp_file = st.file_uploader("Upload Competitor Image", type=["jpg", "png"], key="comp_up")
        
        if st.button("Analyze Competitor 🔍"):
            if comp_file and current_kredi > 0:
                with st.spinner("Decoding competitor strategy..."):
                    base64_img = image_to_base64(comp_file)
                    prompt = "Analyze this competitor's Etsy product. 1. Identify their target keywords. 2. Find weaknesses in their presentation. 3. Suggest how I can outperform them (Price, SEO, or Visuals)."
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}],
                    )
                    st.markdown("### 🏆 How to Beat This Competitor")
                    st.write(response.choices[0].message.content)
                    update_kredi(user_data['id'], current_kredi - 1)
            else:
                st.warning("Upload image or check credits!")

    # --- TAB 3: LISTING SCORE ---
    with tab3:
        st.header("Listing Health Check")
        st.write("Paste your current Title and Tags to get an AI Efficiency Score.")
        user_title = st.text_input("Current Title")
        user_tags = st.text_area("Current Tags (comma separated)")
        
        if st.button("Get Score 📊"):
            if user_title and current_kredi > 0:
                with st.spinner("Calculating score..."):
                    prompt = f"Rate this Etsy Listing SEO out of 100. Title: {user_title}, Tags: {user_tags}. Provide a Score and 3 actionable tips to improve it."
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "You are an Etsy SEO auditor."}, {"role": "user", "content": prompt}],
                    )
                    st.markdown(f"### Result")
                    st.write(response.choices[0].message.content)
                    update_kredi(user_data['id'], current_kredi - 1)
            else:
                st.warning("Please fill the title field!")

if __name__ == "__main__":
    main()
