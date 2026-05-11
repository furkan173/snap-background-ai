import streamlit as st
import base64
from openai import OpenAI
from supabase import create_client

# --- CONFIGURATION & CONNECTIONS ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- USER DATA MANAGEMENT ---
def get_user_data(email):
    res = supabase.table("profiller").select("*").eq("e-posta", email).single().execute()
    return res.data

def update_kredi(user_id, yeni_kredi):
    supabase.table("profiller").update({"krediler": yeni_kredi}).eq("id", user_id).execute()

# --- MAIN APPLICATION ---
def main():
    # Session State Initialization (Persistent results)
    if "seo_result" not in st.session_state:
        st.session_state.seo_result = None

    # Fetch User Data (Targeting the primary account)
    try:
        user_data = get_user_data("furkangunay733@gmail.com")
        current_kredi = user_data['krediler']
    except Exception as e:
        st.error("Error loading user profile. Please check your connection.")
        return

    # --- SIDEBAR (Global Style) ---
    with st.sidebar:
        st.title("💎 EtsyFocus PRO")
        st.metric("Credits Remaining", current_kredi)
        
        st.markdown("---")
        st.subheader("Top Up Credits")
        # Direct Checkout Link (Lemon Squeezy)
        checkout_url = "https://getsnapbackground.lemonsqueezy.com/checkout/buy/a35adaa5-735c-4ffb-936d-442576c4c753"
        st.markdown(f'''
            <a href="{checkout_url}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #FF4B4B; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold;">
                    🔥 Get 100 Credits
                </div>
            </a>
        ''', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("Sign Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- MAIN PANEL (Global UI) ---
    st.title("🚀 AI Etsy SEO Expert")
    st.info("Upload your product photo, and let our AI optimize your SEO strategy instantly.")

    uploaded_file = st.file_uploader("Upload Product Photo", type=["jpg", "jpeg", "png"])
    
    # Customer Guidance Note (Safety & Quality)
    st.caption("⚠️ **For best results:** Use a clear, high-resolution photo on a flat surface. AI may reject images with faces or blurry content for security and quality reasons.")

    lang = st.selectbox("Output Language", ["English", "Turkish", "German", "French", "Spanish"])

    if st.button("Generate SEO Strategy ✨"):
        if not uploaded_file:
            st.warning("Please upload a photo first!")
        elif current_kredi <= 0:
            st.error("Out of credits! Please upgrade in the sidebar to continue.")
        else:
            with st.spinner("AI is analyzing your product and generating strategy..."):
                try:
                    base64_image = image_to_base64(uploaded_file)
                    
                    # Optimized Global Prompt
                    prompt_text = f"""
                    You are an Etsy SEO expert. Analyze the product in this image and provide the following in {lang}:
                    
                    1. **Title**: A high-converting title (max 140 chars).
                    2. **SEO Tags**: 13 powerful, long-tail tags separated by commas.
                    3. **Description**: A short, engaging product description focusing on key benefits.
                    
                    Provide the results directly starting with the Title. No conversational filler.
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
                        max_tokens=600,
                    )

                    # Save result to session
                    st.session_state.seo_result = response.choices[0].message.content
                    
                    # Deduct credit
                    new_kredi = current_kredi - 1
                    update_kredi(user_data['id'], new_kredi)
                    
                    # Success effects and refresh
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

    # --- DISPLAY RESULTS ---
    if st.session_state.seo_result:
        st.success("Analysis Complete!")
        st.markdown("### 📝 AI Generated SEO Results")
        st.text_area("Copy-Paste Ready Data", value=st.session_state.seo_result, height=400)
        
        if st.button("Clear Results"):
            st.session_state.seo_result = None
            st.rerun()

if __name__ == "__main__":
    main()
