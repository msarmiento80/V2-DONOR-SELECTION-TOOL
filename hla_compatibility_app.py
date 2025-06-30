import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import datetime
import os
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="HLA Evaluator",
    page_icon="favicon.png",
    layout="centered"
)

# --- ESTILO PERSONALIZADO ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f8ff;
        color: #000000 !important;
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #000000 !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stAlert, .st-info, .stWarning, .st-error {
        color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- LOGO EN LA INTERFAZ ---
logo_path = "logo_uthc.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
            <img src="data:image/png;base64,{logo_data}" width="200">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("⚠️ No se encontró el archivo del logo (logo_uthc.png). Verifica que esté en el directorio.")

# --- SELECTOR DE IDIOMA ---
idioma = st.selectbox("\U0001F310 Idioma / Language", ["Español", "English"])
T = lambda es, en: es if idioma == "Español" else en

# --- TÍTULOS PRINCIPALES ---
st.title(T("Evaluador de Compatibilidad HLA", "HLA Compatibility Evaluator"))
st.markdown(f"<h4>{T('Programa de Trasplante Hematopoyético del Adulto - Pontificia Universidad Católica de Chile', 'Adult Hematopoietic Transplant Program - Pontifical Catholic University of Chile')}</h4>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-style: italic;'>{T('Esta es una herramienta para ayudar en la decisión del mejor donante una vez haya una selección previa de los potenciales donantes. No reemplaza el adecuado juicio clínico.', 'This is a tool to assist in the selection of the best donor once a pool of potential donors has been preselected. It does not replace appropriate clinical judgment.')}</p>", unsafe_allow_html=True)

# --- MULTIPACIENTES ---
num_pacientes = st.number_input("¿Cuántos pacientes deseas evaluar?", min_value=1, max_value=10, step=1)
resultados = []

for i in range(num_pacientes):
    st.header(f"{T('Paciente', 'Patient')} {i+1}")
    codigo = st.text_input(T("Código del paciente", "Patient code"), key=f"cod_{i}")
    dis_a = st.checkbox("HLA-A", key=f"a_{i}")
    dis_b = st.checkbox("HLA-B", key=f"b_{i}")
    dis_c = st.checkbox("HLA-C", key=f"c_{i}")
    dis_drb1 = st.checkbox("HLA-DRB1", key=f"drb1_{i}")
    dis_dqb1 = st.checkbox("HLA-DQB1", key=f"dqb1_{i}")
    dpb1_no_perm = st.checkbox("HLA-DPB1 no permisivo", key=f"dpb1_{i}")
    lider_tt = st.checkbox("Polimorfismo líder HLA-B T/T", key=f"tt_{i}")

    edad_don = st.number_input(T("Edad del donante", "Donor age"), 0, 75, 30, key=f"edad_{i}")
    grupo_don = st.selectbox("Grupo sanguíneo donante", ["A", "B", "AB", "O"], key=f"gd_{i}")
    grupo_rec = st.selectbox("Grupo sanguíneo receptor", ["A", "B", "AB", "O"], key=f"gr_{i}")
    sexo_don = st.selectbox(T("Sexo del donante", "Donor sex"), ["Masculino", "Femenino"], key=f"sx_{i}")
    hijos_don = st.checkbox(T("Donante con hijos", "Donor has children"), key=f"hx_{i}")
    dsa_valor = st.number_input(T("Nivel de anticuerpos anti-HLA (DSA, MFI)", "Anti-HLA antibodies level (DSA, MFI)"), min_value=0, value=0, key=f"dsa_{i}")

    riesgo = "Bajo"
    if dis_drb1 or dis_b or dpb1_no_perm or lider_tt or sum([dis_a, dis_b, dis_c, dis_drb1, dis_dqb1]) >= 2:
        riesgo = "Alto"
    elif sum([dis_a, dis_b, dis_c, dis_drb1, dis_dqb1]) == 1:
        riesgo = "Intermedio"

    riesgo_gvhd = riesgo
    riesgo_recaida = "Bajo" if riesgo == "Bajo" else ("Intermedio" if edad_don < 40 else "Alto")
    riesgo_prend = "Bajo"
    if dsa_valor > 5000:
        riesgo_prend = "Alto"
    elif grupo_don != grupo_rec:
        riesgo_prend = "Intermedio"
    elif grupo_don != grupo_rec and edad_don > 45:
        riesgo_prend = "Alto"

    prioridad = ""
    if dsa_valor > 5000:
        prioridad = T("Prioridad 3: Donante subóptimo", "Priority 3: Suboptimal donor")
    elif riesgo == "Bajo" and edad_don <= 35 and not lider_tt and grupo_don == grupo_rec and sexo_don == "Masculino":
        prioridad = T("Prioridad 1: Donante ideal", "Priority 1: Optimal donor")
    elif riesgo == "Intermedio" or edad_don <= 50:
        prioridad = T("Prioridad 2: Donante aceptable", "Priority 2: Acceptable donor")
    else:
        prioridad = T("Prioridad 3: Donante subóptimo", "Priority 3: Suboptimal donor")

    recomendacion = ""
    if riesgo_prend == "Alto" and dsa_valor > 5000:
        recomendacion = T("Evitar este donante por riesgo de fallo de prendimiento. Considerar desensibilización.",
                          "Avoid this donor due to graft failure risk. Consider desensitization.")
    elif riesgo == "Alto":
        recomendacion = T("Buscar alternativas si es posible.", "Seek alternatives if possible.")
    elif riesgo == "Intermedio":
        recomendacion = T("Evaluar en comité.", "Evaluate in committee.")
    else:
        recomendacion = T("Proceder si no hay contraindicaciones.", "Proceed if no contraindications exist.")

    resultados.append({
        "Código": codigo,
        "Edad donante": edad_don,
        "Riesgo GVHD": riesgo_gvhd,
        "Riesgo Recaída": riesgo_recaida,
        "Riesgo Prendimiento": riesgo_prend,
        "Prioridad": prioridad,
        "Recomendación": recomendacion
    })

# Mostrar tabla resumen
st.subheader("Resumen de Pacientes")
df = pd.DataFrame(resultados)
st.dataframe(df, use_container_width=True)

# PDF OBLIGATORIO
fecha = datetime.date.today().strftime("%Y-%m-%d")
pdf = FPDF()
for r in resultados:
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, T("Informe de Evaluación HLA", "HLA Evaluation Report"), ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"""
{T('Código del paciente', 'Patient code')}: {r['Código']}
{T('Fecha', 'Date')}: {fecha}

{T('Riesgo de GVHD', 'GVHD Risk')}: {r['Riesgo GVHD']}
{T('Riesgo de recaída', 'Relapse Risk')}: {r['Riesgo Recaída']}
{T('Riesgo de fallo de prendimiento', 'Graft failure risk')}: {r['Riesgo Prendimiento']}

{T('Prioridad del Donante', 'Donor Priority')}: {r['Prioridad']}
{T('Recomendación Clínica', 'Clinical Recommendation')}: {r['Recomendación']}
""")

path = f"/tmp/informe_HLA_multi_{fecha}.pdf"
pdf.output(path)
with open(path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_HLA_multipaciente_{fecha}.pdf">📥 {T("Descargar PDF", "Download PDF")}</a>'
    st.markdown(href, unsafe_allow_html=True)

