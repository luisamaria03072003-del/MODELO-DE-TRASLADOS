 import streamlit as st
import datetime
import math
import requests
import pytz

# Configuración inicial de la página
st.set_page_config(page_title="Disponibilidad Traslado - Ingenio Carmelita", layout="wide")

# Configurar el logo
try:
    st.image("logo.png", width=250)
except FileNotFoundError:
    st.warning("No se encontró el archivo 'logo.png'.")

st.title("Modelo de Disponibilidad de Traslado")

# --- SECCIÓN 1: Entradas Manuales Nuevas ---
st.header("1. Información General")
col1, col2, col3 = st.columns(3)
with col1:
    hacienda_inicial = st.text_input("Hacienda inicial")
with col2:
    hacienda_final = st.text_input("Hacienda final")
with col3:
    frente = st.text_input("Frente")

# --- SECCIÓN 2: Variables Editables (Títulos Verdes del Excel) ---
st.header("2. Variables Operativas")
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    distancia_km = st.number_input("Distancia de traslado km", min_value=0.0, value=45.0, step=1.0)
with col_v2:
    despacho_prom = st.number_input("Despacho prom hora", min_value=1.0, value=75.0, step=1.0)
with col_v3:
    toneladas_disp = st.number_input("Toneladas disponibles", min_value=0.0, value=1200.0, step=10.0)

# --- CÁLCULOS IDÉNTICOS AL EXCEL ---
horas_cana_disp = toneladas_disp / despacho_prom
tiempo_traslado_horas = distancia_km / 20
paradas_tecnicas = max(0, math.floor((distancia_km / 20) - 1))
tiempo_parada_tecnica_min = paradas_tecnicas * 10

colombia_tz = pytz.timezone('America/Bogota')
now = datetime.datetime.now(colombia_tz)

hora_final_estimada = now + datetime.timedelta(hours=(horas_cana_disp - 2))
hora_inicio = hora_final_estimada - datetime.timedelta(hours=tiempo_traslado_horas, minutes=tiempo_parada_tecnica_min)
hora_llegada_apoyo = hora_inicio - datetime.timedelta(minutes=30)

# --- SECCIÓN 3: Resultados (Títulos Amarillos del Excel) ---
st.header("3. Resultados de Estimación")

col_a1, col_a2, col_a3, col_a4 = st.columns(4)
col_a1.metric("Tiempo de parada tecnica", f"{tiempo_parada_tecnica_min} min")
col_a2.metric("Horas de caña disponibles", f"{horas_cana_disp:.2f}")
col_a3.metric("Paradas tecnicas", f"{paradas_tecnicas}")
col_a4.metric("Tiempo de traslados horas", f"{tiempo_traslado_horas:.2f}")

st.divider()

col_h1, col_h2, col_h3 = st.columns(3)
col_h1.info(f"**Hora de llegada de apoyo:**\n{hora_llegada_apoyo.strftime('%Y-%m-%d %I:%M %p')}")
col_h2.success(f"**Hora de inicio:**\n{hora_inicio.strftime('%Y-%m-%d %I:%M %p')}")
col_h3.warning(f"**Hora final estimada:**\n{hora_final_estimada.strftime('%Y-%m-%d %I:%M %p')}")

# --- SECCIÓN 4: Enviar a Google Sheets ---
st.header("4. Guardar Historial")
if st.button("Enviar información a Google Sheets"):
    webhook_url = "https://script.google.com/macros/s/AKfycbzyR-uC9KdNR3_Anyd6mwMvvQSqE1vkZEjwxtZdP9xKfiQorVj3i82oFOaS5wxMvk3W/exec"
    
    row_data = [
        now.strftime('%Y-%m-%d %H:%M:%S'),
        hacienda_inicial,
        hacienda_final,
        frente,
        distancia_km,
        despacho_prom,
        toneladas_disp,
        tiempo_parada_tecnica_min,
        round(horas_cana_disp, 2),
        paradas_tecnicas,
        round(tiempo_traslado_horas, 2),
        hora_llegada_apoyo.strftime('%Y-%m-%d %H:%M:%S'),
        hora_inicio.strftime('%Y-%m-%d %H:%M:%S'),
        hora_final_estimada.strftime('%Y-%m-%d %H:%M:%S')
    ]
    
    with st.spinner("Guardando datos en Google Sheets..."):
        try:
            response = requests.post(webhook_url, json={"row": row_data})
            if response.status_code == 200:
                st.success("¡Datos enviados y guardados en Google Sheets correctamente!")
            else:
                st.error(f"Error al guardar los datos. Código de respuesta: {response.status_code}")
        except Exception as e:
            st.error(f"Se produjo un error de conexión: {e}")
