import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import datetime
fecha = datetime.date.today().strftime("%Y-%m-%d")
import os

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
        <div style=\"display: flex; justify-content: center; margin-bottom: 1rem;\">
            <img src=\"data:image/png;base64,{logo_data}\" width=\"200\">
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

# --- FORMULARIO MULTIPACIENTE ---
st.markdown("\n---\n")
st.markdown("### 🧾 Evaluación de pacientes")

num_pacientes = st.number_input("Cantidad de pacientes a ingresar:", min_value=1, value=1)

pacientes = []

# Función para colorear niveles de riesgo como texto
colores = {"Bajo": (0, 128, 0), "Intermedio": (255, 165, 0), "Alto": (220, 20, 60)}

for i in range(num_pacientes):
    st.markdown(f"#### Paciente {i+1}")
    codigo = st.text_input(f"Código del paciente {i+1}", key=f"codigo_{i}")
    edad_don = st.number_input(f"Edad del donante (Paciente {i+1})", min_value=0, max_value=100, key=f"edad_{i}")
    grupo_don = st.selectbox(f"Grupo sanguíneo donante (Paciente {i+1})", ["A", "B", "AB", "O"], key=f"grupo_don_{i}")
    grupo_rec = st.selectbox(f"Grupo sanguíneo receptor (Paciente {i+1})", ["A", "B", "AB", "O"], key=f"grupo_rec_{i}")
    sexo_don = st.selectbox(f"Sexo del donante (Paciente {i+1})", ["Masculino", "Femenino"], key=f"sexo_{i}")
    hijos_don = st.checkbox(f"Donante con hijos (Paciente {i+1})", key=f"hijos_{i}")
    dsa_valor = st.number_input(f"Nivel de DSA (MFI) (Paciente {i+1})", min_value=0, key=f"dsa_{i}")

    dis_a = st.checkbox(f"HLA-A (Paciente {i+1})", key=f"a_{i}")
    dis_b = st.checkbox(f"HLA-B (Paciente {i+1})", key=f"b_{i}")
    dis_c = st.checkbox(f"HLA-C (Paciente {i+1})", key=f"c_{i}")
    dis_drb1 = st.checkbox(f"HLA-DRB1 (Paciente {i+1})", key=f"drb1_{i}")
    dis_dqb1 = st.checkbox(f"HLA-DQB1 (Paciente {i+1})", key=f"dqb1_{i}")
    dpb1_no_perm = st.checkbox(f"HLA-DPB1 no permisivo (Paciente {i+1})", key=f"dpb1_{i}")
    lider_tt = st.checkbox(f"Polimorfismo líder HLA-B T/T (Paciente {i+1})", key=f"lider_{i}")

    riesgo_gvhd = "Bajo"
    if dis_drb1 or dis_b or dpb1_no_perm or lider_tt or sum([dis_a, dis_b, dis_c, dis_drb1, dis_dqb1]) >= 2:
        riesgo_gvhd = "Alto"
    elif sum([dis_a, dis_b, dis_c, dis_drb1, dis_dqb1]) == 1:
        riesgo_gvhd = "Intermedio"

    riesgo_recaida = "Bajo" if riesgo_gvhd == "Bajo" else ("Intermedio" if edad_don < 40 else "Alto")

    riesgo_prend = "Bajo"
    if dsa_valor > 5000:
        riesgo_prend = "Alto"
    elif grupo_don != grupo_rec and edad_don > 45:
        riesgo_prend = "Alto"
    elif grupo_don != grupo_rec:
        riesgo_prend = "Intermedio"

    riesgo_dsa = "Negativo"
    if dsa_valor > 2000:
        riesgo_dsa = "Positivo (>2000 MFI)"

    prioridad = ""
    if dsa_valor > 5000:
        prioridad = T("Prioridad 3: Donante subóptimo", "Priority 3: Suboptimal donor")
    elif riesgo_gvhd == "Bajo" and edad_don <= 35 and not lider_tt and grupo_don == grupo_rec and sexo_don == "Masculino":
        prioridad = T("Prioridad 1: Donante ideal", "Priority 1: Optimal donor")
    elif riesgo_gvhd == "Intermedio" or edad_don <= 50:
        prioridad = T("Prioridad 2: Donante aceptable", "Priority 2: Acceptable donor")
    else:
        prioridad = T("Prioridad 3: Donante subóptimo", "Priority 3: Suboptimal donor")

    recomendacion = ""
    if riesgo_prend == "Alto" and dsa_valor > 5000:
        recomendacion = T(
            "Se recomienda evitar este donante debido al alto riesgo de fallo de prendimiento asociado a anticuerpos anti-HLA elevados (>5000 MFI). Si se considera imprescindible, debe evaluarse desensibilización pre-trasplante.",
            "Avoid this donor due to high graft failure risk associated with elevated anti-HLA antibodies (>5000 MFI). If this donor must be used, consider pre-transplant desensitization strategies."
        )
    elif riesgo_gvhd == "Alto":
        recomendacion = T(
            "Buscar alternativas si es posible; alto riesgo por incompatibilidades HLA.",
            "Seek alternatives if possible; high risk due to HLA incompatibilities."
        )
    elif riesgo_gvhd == "Intermedio":
        recomendacion = T(
            "Evaluar en comité; riesgo intermedio.",
            "Evaluate in committee; intermediate risk."
        )
    else:
        recomendacion = T(
            "Proceder si no existen otras contraindicaciones.",
            "Proceed if no other contraindications exist."
        )

    pacientes.append({
        "Código": codigo,
        "Edad donante": edad_don,
        "DSA": dsa_valor,
        "Riesgo GVHD": riesgo_gvhd,
        "Riesgo recaída": riesgo_recaida,
        "Riesgo prendimiento": riesgo_prend,
        "Compatibilidad ABO": "Compatible" if grupo_don == grupo_rec else "Incompatible",
        "Prioridad": prioridad,
        "Recomendación clínica": recomendacion
    })

# Mostrar resumen por paciente
st.subheader(T("Resumen por paciente", "Patient summary"))
df_pacientes = pd.DataFrame(pacientes)
st.dataframe(df_pacientes, use_container_width=True)

# Generar PDF con recomendaciones y riesgo coloreado
if st.button("📄 Generar informe PDF"):
    pdf = FPDF()
    pdf.add_page()

    if os.path.exists(logo_path):
        pdf.image(logo_path, x=85, w=40)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Informe Evaluación HLA", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)

    for p in pacientes:
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 8, f"Código: {p['Código']}")
        pdf.multi_cell(0, 8, f"Edad donante: {p['Edad donante']}")
        pdf.multi_cell(0, 8, f"DSA (MFI): {p['DSA']}")

        pdf.set_text_color(*colores.get(p['Riesgo GVHD'], (0, 0, 0)))
        pdf.multi_cell(0, 8, f"Riesgo GVHD: {p['Riesgo GVHD']}")

        pdf.set_text_color(*colores.get(p['Riesgo recaída'], (0, 0, 0)))
        pdf.multi_cell(0, 8, f"Riesgo de recaída: {p['Riesgo recaída']}")

        pdf.set_text_color(*colores.get(p['Riesgo prendimiento'], (0, 0, 0)))
        pdf.multi_cell(0, 8, f"Riesgo de prendimiento: {p['Riesgo prendimiento']}")

        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 8, f"Compatibilidad ABO: {p['Compatibilidad ABO']}")
        pdf.multi_cell(0, 8, f"{p['Prioridad']}")
        pdf.multi_cell(0, 8, f"Recomendación: {p['Recomendación clínica']}")
        pdf.ln(5)

    path = "/tmp/informe_hla_pacientes.pdf"
    pdf.output(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="informe_hla_pacientes.pdf">📥 Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
        
