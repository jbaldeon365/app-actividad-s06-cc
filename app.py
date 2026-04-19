import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd

# -------------------------
# CONEXIÓN MONGODB ATLAS
# -------------------------
uri = "mongodb+srv://josebaldeon365_db_user:im3v8WmvvbmghmkV@cluster0.dslhgkt.mongodb.net/"

client = MongoClient(uri)

db = client["banco_bra"]
coleccion = db["creditos"]

# -------------------------
# TÍTULO
# -------------------------
st.title("Sistema Inteligente de Evaluación de Créditos - Banco Regional Andino")

# -------------------------
# FORMULARIO
# -------------------------
nombre = st.text_input("Nombre del cliente")
dni = st.text_input("DNI")
ingreso = st.number_input("Ingreso mensual", min_value=0)
antiguedad = st.number_input("Antigüedad laboral (meses)", min_value=0)
deuda = st.number_input("Deuda actual", min_value=0)
monto = st.number_input("Monto solicitado", min_value=0)

# -------------------------
# BOTÓN EVALUAR
# -------------------------
if st.button("Evaluar crédito"):

    if nombre and dni:

        if ingreso > 2500 and antiguedad >= 12 and deuda < ingreso * 0.4:
            resultado = "Aprobado"
        elif ingreso > 1500:
            resultado = "Observado"
        else:
            resultado = "Rechazado"

        datos = {
            "nombre": nombre,
            "dni": dni,
            "ingreso": ingreso,
            "antiguedad": antiguedad,
            "deuda": deuda,
            "monto": monto,
            "resultado": resultado,
            "fecha": datetime.now()
        }

        coleccion.insert_one(datos)

        st.success(f"Resultado: {resultado}")

    else:
        st.warning("Complete nombre y DNI")

# -------------------------
# HISTORIAL
# -------------------------
st.subheader("Historial de Solicitudes")

datos = list(coleccion.find({}, {"_id": 0}))

if datos:
    df = pd.DataFrame(datos)
    st.dataframe(df, use_container_width=True)
else:
    st.write("No hay registros aún")