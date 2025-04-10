import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Concrete Mix Bot", layout="centered")
st.title("🧱 Concrete Mix Design Calculator (IS 10262:2019)")

st.markdown("### 🔢 Input Parameters")

# User inputs
grade = st.selectbox("Select Grade of Concrete", ["M10", "M15", "M20", "M25", "M30", "M35", "M40"])
cement_type = st.selectbox("Cement Type", ["OPC 33", "OPC 43", "OPC 53", "PPC"])
max_agg_size = st.selectbox("Maximum Aggregate Size (mm)", [10, 20])
exposure = st.selectbox("Exposure Condition", ["Mild", "Moderate", "Severe", "Very Severe", "Extreme"])
w_c_ratio = st.number_input("Water-Cement Ratio", min_value=0.3, max_value=0.7, step=0.01, value=0.5)
workability = st.slider("Workability (Slump in mm)", 25, 150, 75)
density = st.number_input("Concrete Density (kg/m³)", min_value=2200, max_value=2600, step=10, value=2400)

st.markdown("### 🌊 Moisture & Absorption Corrections")

moisture_fa = st.number_input("Moisture content - Fine Aggregate (%)", min_value=0.0, max_value=10.0, step=0.1, value=2.0)
moisture_ca = st.number_input("Moisture content - Coarse Aggregate (%)", min_value=0.0, max_value=10.0, step=0.1, value=1.0)
absorption_fa = st.number_input("Water absorption - Fine Aggregate (%)", min_value=0.0, max_value=5.0, step=0.1, value=1.0)
absorption_ca = st.number_input("Water absorption - Coarse Aggregate (%)", min_value=0.0, max_value=5.0, step=0.1, value=0.5)

st.markdown("### 🧪 Admixture & SCM Options")

use_admixture = st.checkbox("Use Chemical Admixture?")
if use_admixture:
    admixture_type = st.selectbox("Admixture Type", ["Plasticizer", "Superplasticizer"])
    admixture_dosage = st.number_input("Admixture Dosage (% of cement)", min_value=0.0, max_value=5.0, step=0.1, value=1.0)

use_scm = st.checkbox("Use Supplementary Cementitious Material (SCM)?")
if use_scm:
    scm_type = st.selectbox("SCM Type", ["Fly Ash", "GGBS"])
    scm_percentage = st.number_input("SCM Replacement (% of total cement)", min_value=0.0, max_value=70.0, step=5.0, value=30.0)

st.markdown("### 💸 Cost & CO₂ Estimation")

cost_cement = st.number_input("Cement cost (₹/kg)", value=7.0)
cost_fa = st.number_input("Fine Aggregate cost (₹/kg)", value=1.0)
cost_ca = st.number_input("Coarse Aggregate cost (₹/kg)", value=0.8)
cost_water = st.number_input("Water cost (₹/litre)", value=0.005)
cost_admixture = st.number_input("Admixture cost (₹/kg)", value=40.0)
cost_scm = st.number_input("SCM cost (₹/kg)", value=2.5)

co2_cement = st.number_input("CO₂ emission - Cement (kg CO₂/kg)", value=0.9)
co2_fa = st.number_input("CO₂ emission - Fine Aggregate (kg CO₂/kg)", value=0.005)
co2_ca = st.number_input("CO₂ emission - Coarse Aggregate (kg CO₂/kg)", value=0.005)
co2_water = st.number_input("CO₂ emission - Water (kg CO₂/litre)", value=0.0003)
co2_scm = st.number_input("CO₂ emission - SCM (kg CO₂/kg)", value=0.2)
co2_admixture = st.number_input("CO₂ emission - Admixture (kg CO₂/kg)", value=1.5)

optimize = st.checkbox("✨ Suggest Better Mix (Optimization Mode)")

if st.button("Calculate Mix Design"):
    grade_dict = {"M10": 10, "M15": 15, "M20": 20, "M25": 25, "M30": 30, "M35": 35, "M40": 40}
    fck = grade_dict[grade]

    def compute_mix(w_c, scm_pct):
        water = 186
        cement = round(water / w_c, 1)
        if scm_pct > 0:
            scm_amount = round(cement * scm_pct / 100, 1)
            cement = round(cement - scm_amount, 1)
        else:
            scm_amount = 0

        admixture_qty = round(cement * admixture_dosage / 100, 1) if use_admixture else 0
        fine_agg = round(0.35 * density, 1)
        coarse_agg = round(0.65 * density, 1)
        extra_water_fa = fine_agg * (moisture_fa - absorption_fa) / 100
        extra_water_ca = coarse_agg * (moisture_ca - absorption_ca) / 100
        adjusted_water = round(water + extra_water_fa + extra_water_ca, 1)

        total_cost = (
            cement * cost_cement +
            fine_agg * cost_fa +
            coarse_agg * cost_ca +
            adjusted_water * cost_water +
            admixture_qty * cost_admixture +
            scm_amount * cost_scm
        )
        total_co2 = (
            cement * co2_cement +
            fine_agg * co2_fa +
            coarse_agg * co2_ca +
            adjusted_water * co2_water +
            admixture_qty * co2_admixture +
            scm_amount * co2_scm
        )
        return {
            'cement': cement,
            'scm': scm_amount,
            'water': adjusted_water,
            'fa': fine_agg,
            'ca': coarse_agg,
            'admixture': admixture_qty,
            'cost': total_cost,
            'co2': total_co2,
            'w_c': w_c,
            'scm_pct': scm_pct
        }

    best_mix = compute_mix(w_c_ratio, scm_percentage if use_scm else 0)

    if optimize:
        st.info("🔎 Running optimization for best cost/CO₂ balance...")
        results = []
        for w_c_try in [round(w_c_ratio + i * 0.01, 2) for i in range(-2, 3)]:
            if 0.3 <= w_c_try <= 0.7:
                for scm_try in range(0, 51, 10):
                    mix = compute_mix(w_c_try, scm_try)
                    if mix['cement'] >= 300 and mix['w_c'] <= 0.6:
                        results.append(mix)
        if results:
            best_mix = min(results, key=lambda x: x['cost'])
            st.success(f"✅ Suggested Mix: W/C = {best_mix['w_c']}, SCM = {best_mix['scm_pct']}% → ₹{round(best_mix['cost'],2)} / {round(best_mix['co2'],2)} kg CO₂")

    st.markdown("### 📋 Mix Design Output")
    st.markdown(f"*Water-Cement Ratio:* {best_mix['w_c']}")
    st.markdown(f"*Cement:* {best_mix['cement']} kg/m³")
    st.markdown(f"*SCM:* {best_mix['scm']} kg/m³")
    st.markdown(f"*Water (Adjusted):* {best_mix['water']} kg/m³")
    st.markdown(f"*Fine Aggregate:* {best_mix['fa']} kg/m³")
    st.markdown(f"*Coarse Aggregate:* {best_mix['ca']} kg/m³")
    st.markdown(f"*Admixture:* {best_mix['admixture']} kg/m³")
    st.markdown(f"### 💰 Total Cost: ₹{round(best_mix['cost'], 2)}")
    st.markdown(f"### 🌱 Total CO₂: {round(best_mix['co2'], 2)} kg")

    mix_labels = ['Cement', 'SCM', 'Water', 'Fine Agg', 'Coarse Agg', 'Admixture']
    mix_values = [best_mix['cement'], best_mix['scm'], best_mix['water'], best_mix['fa'], best_mix['ca'], best_mix['admixture']]

    fig1, ax1 = plt.subplots()
    ax1.pie(mix_values, labels=mix_labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

    df_cost = pd.DataFrame({
        'Material': mix_labels,
        'Cost (₹)': [
            best_mix['cement'] * cost_cement,
            best_mix['scm'] * cost_scm,
            best_mix['water'] * cost_water,
            best_mix['fa'] * cost_fa,
            best_mix['ca'] * cost_ca,
            best_mix['admixture'] * cost_admixture
        ]
    })
    st.bar_chart(df_cost.set_index('Material'))

    df_co2 = pd.DataFrame({
        'Material': mix_labels,
        'CO₂ (kg)': [
            best_mix['cement'] * co2_cement,
            best_mix['scm'] * co2_scm,
            best_mix['water'] * co2_water,
            best_mix['fa'] * co2_fa,
            best_mix['ca'] * co2_ca,
            best_mix['admixture'] * co2_admixture
        ]
    })
    st.bar_chart(df_co2.set_index('Material'))
