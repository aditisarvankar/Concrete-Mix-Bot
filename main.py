import streamlit as st

st.set_page_config(page_title="Concrete Mix Design Bot", layout="centered")

st.title("🧱 Concrete Mix Design Calculator (IS 10262:2019)")
st.markdown("### Enter Your Requirements")

# User Inputs
grade = st.selectbox("Select Grade of Concrete", ["M15", "M20", "M25", "M30", "M35", "M40"])
cement_type = st.selectbox("Cement Type", ["OPC 43", "OPC 53", "PPC", "PSC"])
max_aggregate_size = st.selectbox("Maximum Aggregate Size (mm)", [10, 20])
exposure = st.selectbox("Exposure Condition", ["Mild", "Moderate", "Severe", "Very Severe", "Extreme"])
workability = st.slider("Desired Workability (Slump in mm)", 25, 150, 100)
water_cement_ratio = st.number_input("Water-Cement Ratio", min_value=0.3, max_value=0.7, value=0.5, step=0.01)
cement_content = st.number_input("Cement Content (kg/m³)", min_value=300, max_value=500, value=360, step=10)
water_content = round(cement_content * water_cement_ratio, 1)

# Simplified Mix Design (Basic Estimates)
if grade == "M15":
    mix_ratio = "1 : 2 : 4"
    total_parts = 7
elif grade == "M20":
    mix_ratio = "1 : 1.5 : 3"
    total_parts = 5.5
elif grade == "M25":
    mix_ratio = "1 : 1 : 2"
    total_parts = 4
elif grade == "M30":
    mix_ratio = "1 : 0.8 : 1.6"
    total_parts = 3.4
elif grade == "M35":
    mix_ratio = "1 : 0.6 : 1.2"
    total_parts = 2.8
else:
    mix_ratio = "1 : 0.5 : 1"
    total_parts = 2.5

# Dry volume = 1.54 times wet volume
dry_volume = 1.54

# Calculations (Simplified)
cement = cement_content
water = water_content
fine_agg = round((cement * dry_volume * eval(mix_ratio.split(":")[1])) / total_parts, 1)
coarse_agg = round((cement * dry_volume * eval(mix_ratio.split(":")[2])) / total_parts, 1)

if st.button("Calculate Mix Design"):
    st.success("🔎 Mix Design Result:")
    st.markdown(f"*Grade of Concrete:* {grade}")
    st.markdown(f"*Mix Ratio (C : FA : CA):* {mix_ratio}")
    st.markdown(f"*Cement Content:* {cement} kg/m³")
    st.markdown(f"*Water Content:* {water} kg/m³")
    st.markdown(f"*Fine Aggregate:* {fine_agg} kg/m³")
    st.markdown(f"*Coarse Aggregate:* {coarse_agg} kg/m³")
    st.markdown("*Note:* This is a simplified estimation based on IS 10262:2019. For structural design, lab trials are necessary.")