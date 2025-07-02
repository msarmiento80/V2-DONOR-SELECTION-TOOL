
import pandas as pd
import matplotlib.pyplot as plt
import os

def ejecutar_formulario_completo(st, T, fecha, logo_path):
    num_pacientes = st.number_input("Cantidad de pacientes a ingresar:", min_value=1, value=1)
    pacientes = []

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
                "Se recomienda evitar este donante debido al alto riesgo de fallo de prendimiento asociado a anticuerpos anti-HLA elevados (>5000 MFI).",
                "Avoid this donor due to high graft failure risk associated with elevated anti-HLA antibodies (>5000 MFI)."
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

    # Tabla de referencia
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

    st.subheader(T("🔍 Evidencia inmunogenética clave en la selección de donantes", "🔍 Key immunogenetic evidence in donor selection"))
    st.dataframe(tabla_ref.set_index("Ranking"), use_container_width=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')
    tabla = ax.table(cellText=tabla_ref.values,
                     colLabels=tabla_ref.columns,
                     loc='center', cellLoc='center')
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(8)
    tabla.scale(1, 1.5)
    pdf_tabla_path = f"/tmp/tabla_inmunogenetica_{fecha}.png"
    plt.savefig(pdf_tabla_path, bbox_inches='tight')
    plt.close()

    return pacientes, tabla_ref, pdf_tabla_path
