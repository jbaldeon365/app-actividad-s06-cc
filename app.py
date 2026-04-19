import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import certifi

# -------------------------
# CONFIGURACIÓN
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
st.title("Portal Digital de Créditos - Banco Regional Andino")

# -------------------------
# TABS
# -------------------------
tab1, tab2 = st.tabs(["Cliente Digital", "Panel Bancario"])

# ======================================================
# TAB CLIENTE DIGITAL
# ======================================================
with tab1:

    st.subheader("Solicita tu crédito en línea")

    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre completo")
        dni = st.text_input("DNI")
        ingreso = st.number_input("Ingreso mensual", min_value=0)

    with col2:
        antiguedad = st.number_input("Antigüedad laboral (meses)", min_value=0)
        deuda = st.number_input("Deuda actual", min_value=0)
        monto = st.number_input("Monto solicitado", min_value=0)

    if st.button("Enviar solicitud"):

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

            monto_recomendado = ingreso * 5

            if score >= 80:
                resultado = "Preaprobado"
                mensaje = "Tu crédito fue preaprobado digitalmente"
            elif score >= 50:
                resultado = "En evaluación"
                mensaje = "Tu solicitud requiere validación adicional"
            else:
                resultado = "No aprobado"
                mensaje = "Tu perfil necesita revisión"

            datos = {
                "nombre": nombre,
                "dni": dni,
                "ingreso": ingreso,
                "antiguedad": antiguedad,
                "deuda": deuda,
                "monto": monto,
                "score": score,
                "resultado": resultado,
                "fecha": datetime.now()
            }

            coleccion.insert_one(datos)

            st.success(mensaje)
            st.info(f"Score crediticio: {score}/100")
            st.info(f"Monto sugerido: S/ {monto_recomendado}")
            st.metric("Tiempo de respuesta", "2 segundos")

            st.rerun()

# ======================================================
# TAB PANEL BANCARIO
# ======================================================
with tab2:

    st.subheader("Panel de monitoreo bancario")

    datos_db = list(coleccion.find({}, {"_id": 0}))
    df = pd.DataFrame(datos_db)

    if not df.empty:

        c1, c2, c3 = st.columns(3)

        c1.metric("Solicitudes Totales", len(df))
        c2.metric("Preaprobados", len(df[df["resultado"] == "Preaprobado"]))
        c3.metric("En evaluación", len(df[df["resultado"] == "En evaluación"]))

        st.subheader("Buscar por DNI")

        dni_buscar = st.text_input("Ingrese DNI")

        if dni_buscar:
            filtro = df[df["dni"] == dni_buscar]

            if not filtro.empty:
                st.dataframe(filtro, use_container_width=True)
            else:
                st.write("Cliente no encontrado")

        st.subheader("Historial General")
        st.dataframe(df, use_container_width=True)

        st.subheader("Distribución de solicitudes")

        conteo = df["resultado"].value_counts()
        st.bar_chart(conteo)

    else:
        st.write("No hay solicitudes registradas")