import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import certifi
import matplotlib.pyplot as plt

# -------------------------
# CONFIGURACIÓN GENERAL
# -------------------------
st.set_page_config(page_title="Banco Regional Andino", layout="wide")

# -------------------------
# CONEXIÓN MONGODB ATLAS
# -------------------------
uri = "mongodb+srv://josebaldeon365_db_user:im3v8WmvvbmghmkV@cluster0.dslhgkt.mongodb.net/"

client = MongoClient(uri, tlsCAFile=certifi.where())

db = client["banco_bra"]
coleccion = db["creditos"]

# -------------------------
# TÍTULO
# -------------------------
st.title("Sistema Inteligente de Evaluación Digital de Créditos")
st.caption("Caso: Banco Regional Andino")

# -------------------------
# MÉTRICAS GENERALES
# -------------------------
datos_db = list(coleccion.find({}, {"_id": 0}))
df = pd.DataFrame(datos_db) if datos_db else pd.DataFrame()

if not df.empty:
    total = len(df)
    aprobados = len(df[df["resultado"] == "Aprobado"])
    observados = len(df[df["resultado"] == "Observado"])
    rechazados = len(df[df["resultado"] == "Rechazado"])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Solicitudes", total)
    c2.metric("Aprobados", aprobados)
    c3.metric("Observados", observados)
    c4.metric("Rechazados", rechazados)

# -------------------------
# FORMULARIO
# -------------------------
st.subheader("Nueva Solicitud de Crédito")

col1, col2 = st.columns(2)

with col1:
    nombre = st.text_input("Nombre del cliente")
    dni = st.text_input("DNI")
    ingreso = st.number_input("Ingreso mensual", min_value=0)

with col2:
    antiguedad = st.number_input("Antigüedad laboral (meses)", min_value=0)
    deuda = st.number_input("Deuda actual", min_value=0)
    monto = st.number_input("Monto solicitado", min_value=0)

# -------------------------
# SCORE CREDITICIO
# -------------------------
if st.button("Evaluar crédito"):

    if nombre and dni:

        score = 0

        if ingreso > 3000:
            score += 40
        elif ingreso > 2000:
            score += 25

        if antiguedad >= 12:
            score += 30

        if deuda < ingreso * 0.3:
            score += 30

        if score >= 80:
            resultado = "Aprobado"
            riesgo = "Bajo"
        elif score >= 50:
            resultado = "Observado"
            riesgo = "Medio"
        else:
            resultado = "Rechazado"
            riesgo = "Alto"

        datos = {
            "nombre": nombre,
            "dni": dni,
            "ingreso": ingreso,
            "antiguedad": antiguedad,
            "deuda": deuda,
            "monto": monto,
            "score": score,
            "riesgo": riesgo,
            "resultado": resultado,
            "fecha": datetime.now()
        }

        coleccion.insert_one(datos)

        st.success(f"Resultado: {resultado}")
        st.info(f"Score crediticio: {score}/100")
        st.warning(f"Nivel de riesgo: {riesgo}")

    else:
        st.warning("Complete nombre y DNI")

# -------------------------
# BÚSQUEDA POR DNI
# -------------------------
st.subheader("Buscar cliente por DNI")

dni_buscar = st.text_input("Ingrese DNI para buscar")

if dni_buscar:
    resultado_busqueda = list(coleccion.find({"dni": dni_buscar}, {"_id": 0}))

    if resultado_busqueda:
        df_busqueda = pd.DataFrame(resultado_busqueda)
        st.dataframe(df_busqueda, use_container_width=True)
    else:
        st.write("Cliente no encontrado")

# -------------------------
# HISTORIAL GENERAL
# -------------------------
st.subheader("Historial General")

if not df.empty:
    st.dataframe(df, use_container_width=True)

# -------------------------
# GRÁFICO
# -------------------------
st.subheader("Distribución de resultados")

if not df.empty:
    conteo = df["resultado"].value_counts()

    fig, ax = plt.subplots()
    ax.bar(conteo.index, conteo.values)

    st.pyplot(fig)