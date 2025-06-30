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

# --- TABLA INFORMATIVA CON REFERENCIAS ---
st.markdown("""
### 🔍 Evidencia inmunogenética clave en la selección de donantes
""")
tabla_ref = pd.DataFrame({
    "Ranking": ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"],
    "Factor": [
        "HLA-DRB1 mismatch",
        "HLA-A or HLA-B mismatch",
        "Non-permissive HLA-DPB1",
        "HLA-C mismatch",
        "HLA-DQB1 mismatch",
        "HLA-B leader (M/T)",
        "HLA-DQA1 mismatch",
        "KIR ligand mismatch",
        "Allelic vs Antigen mismatch",
        "Mismatch directionality"
    ],
    "Impacto clínico": [
        "↑ Acute GVHD, ↓ OS, ↑ TRM",
        "↑ GVHD, graft failure, ↓ survival",
        "↑ GVHD, ↑ TRM",
        "↑ chronic GVHD, moderate TRM",
        "Limited effect alone; augments DRB1",
        "↑ relapse if mismatch (T/T donor)",
        "Emerging evidence; CD4 repertoire",
        "↓ relapse, NK alloreactivity (AML)",
        "Allele mismatch worse than antigen",
        "GVHD (GVH), graft loss (HVG)"
    ],
    "N° Pacientes": ["12000", "18000", "5000", "4000", "6000", "7000", "3000", "3500", "10000", "4000"],
    "Fuerza Evidencia": ["Muy Alta", "Muy Alta", "Alta", "Alta", "Media", "Media", "Baja", "Media", "Alta", "Media"],
    "Referencia": [
        "Lee SJ et al. (2007)",
        "Morishima Y et al. (2015)",
        "Fleischhauer K et al. (2012)",
        "Petersdorf EW et al. (2001)",
        "Kawase T et al. (2007)",
        "Pidala J et al. (2020)",
        "Madbouly AS et al. (2016)",
        "Ruggeri L et al. (2002)",
        "Petersdorf EW et al. (2001)",
        "Dehn J et al. (2014)"
    ]
})
st.dataframe(tabla_ref.set_index("Ranking"), use_container_width=True)

# --- GUARDAR TABLA COMO IMAGEN PARA PDF ---
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')
tabla = ax.table(cellText=tabla_ref.values,
                 colLabels=tabla_ref.columns,
                 loc='center', cellLoc='center')
tabla.auto_set_font_size(False)
tabla.set_fontsize(8)
tabla.scale(1, 1.5)
pdf_tabla_path = f"/tmp/tabla_inmunogenetica.png"
plt.savefig(pdf_tabla_path, bbox_inches='tight')
plt.close()

# Aquí se integrará el ingreso de múltiples pacientes y PDF obligatorio
