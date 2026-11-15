import streamlit as st
import datetime
import math
import json
import urllib.request
import base64
import os

# Configuración inicial de la página
st.set_page_config(
    page_title="Disponibilidad de Traslado - Ingenio Carmelita",
    page_icon="🌿",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS (ESTÉTICA INGENIO CARMELITA + EXCEL) ---
st.markdown("""
<style>
    /* Fondo general suave con tono cañero */
    .stApp {
        background-color: #F4F7F2;
    }
    /* Encabezado principal */
    .header-banner {
        background: linear-gradient(135deg, #14452F 0%, #246A3E 55%, #388E3C 100%);
        padding: 22px 30px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 6px 18px rgba(20, 69, 47, 0.22);
        margin-bottom: 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 5px solid #FBC02D;
    }
    .header-text {
        text-align: center;
        flex: 1;
    }
    .header-text h1 {
        color: #FFFFFF;
        font-size: 2.05rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .header-text p {
        color: #E8F5E9;
        font-size: 1.05rem;
        margin: 6px 0 0 0;
        font-weight: 500;
    }
    /* Contenedor del logo centrado y grande */
    .logo-box {
        background-color: #FFFFFF;
        border-radius: 14px;
        padding: 14px 28px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 16px;
        border: 1px solid #DCE7D9;
    }
    /* Títulos de sección estilo Excel (Verde y Amarillo) */
    .sec-header-info {
        background-color: #1B5E20;
        color: #FFFFFF;
        padding: 10px 16px;
        border-radius: 10px 10px 0 0;
        font-weight: 700;
        font-size: 1.05rem;
        letter-spacing: 0.3px;
    }
    .sec-header-verde {
        background-color: #2E7D32;
        color: #FFFFFF;
        padding: 10px 16px;
        border-radius: 10px 10px 0 0;
        font-weight: 700;
        font-size: 1.05rem;
        border-bottom: 3px solid #A5D6A7;
    }
    .sec-header-amarillo {
        background-color: #FFF176;
        color: #1F2937;
        padding: 10px 16px;
        border-radius: 10px 10px 0 0;
        font-weight: 800;
        font-size: 1.05rem;
        border-bottom: 3px solid #FBC02D;
    }
    /* Tarjetas de resultados amarillas */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        overflow: hidden;
        margin-bottom: 14px;
        text-align: center;
    }
    .kpi-title-yellow {
        background-color: #FFFF66;
        color: #111827;
        font-weight: 700;
        font-size: 0.92rem;
        padding: 8px 10px;
        border-bottom: 1px solid #E6E600;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #14452F;
        padding: 14px 10px 4px 10px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #6B7280;
        padding-bottom: 10px;
    }
    /* Tarjetas de horarios */
    .time-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 3px 10px rgba(0,0,0,0.06);
        overflow: hidden;
        text-align: center;
        margin-bottom: 12px;
    }
    .time-value {
        font-size: 1.25rem;
        font-weight: 800;
        color: #111827;
        padding: 14px 8px 4px 8px;
    }
    .time-date {
        font-size: 0.85rem;
        font-weight: 600;
        color: #2E7D32;
        padding-bottom: 12px;
    }
    /* Botón principal */
    div.stButton > button {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
        color: white;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.65rem 1.2rem;
        border-radius: 10px;
        border: none;
        width: 100%;
        box-shadow: 0 4px 10px rgba(27, 94, 32, 0.25);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #14452F 0%, #1B5E20 100%);
        color: #FFFF66;
    }
</style>
""", unsafe_allow_html=True)

# --- SVG DE CAÑITAS DE AZÚCAR ---
SVG_CANITAS = """
<svg width="78" height="92" viewBox="0 0 90 110" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Hojas de caña izquierda -->
  <path d="M32 38 C14 28, 6 34, 4 44 C14 38, 24 38, 32 43 Z" fill="#A5D6A7"/>
  <path d="M32 62 C12 54, 4 62, 2 72 C13 64, 23 64, 32 68 Z" fill="#81C784"/>
  <!-- Tallo izquierdo -->
  <rect x="30" y="14" width="9" height="86" rx="4" fill="#C5E1A5" stroke="#558B2F" stroke-width="1.5"/>
  <line x1="30" y1="34" x2="39" y2="34" stroke="#33691E" stroke-width="2.5"/>
  <line x1="30" y1="56" x2="39" y2="56" stroke="#33691E" stroke-width="2.5"/>
  <line x1="30" y1="78" x2="39" y2="78" stroke="#33691E" stroke-width="2.5"/>
  <!-- Hojas superiores -->
  <path d="M34 16 C26 4, 16 4, 10 10 C19 9, 27 12, 33 19 Z" fill="#AED581"/>
  <path d="M54 12 C64 2, 76 3, 82 10 C72 8, 63 10, 55 16 Z" fill="#AED581"/>
  <!-- Hojas de caña derecha -->
  <path d="M56 44 C74 34, 84 40, 86 50 C76 44, 66 44, 56 49 Z" fill="#A5D6A7"/>
  <path d="M56 70 C76 62, 84 70, 86 80 C75 72, 65 72, 56 76 Z" fill="#81C784"/>
  <!-- Tallo derecho -->
  <rect x="48" y="8" width="10" height="92" rx="4.5" fill="#DCE775" stroke="#689F38" stroke-width="1.5"/>
  <line x1="48" y1="28" x2="58" y2="28" stroke="#33691E" stroke-width="2.5"/>
  <line x1="48" y1="50" x2="58" y2="50" stroke="#33691E" stroke-width="2.5"/>
  <line x1="48" y1="72" x2="58" y2="72" stroke="#33691E" stroke-width="2.5"/>
</svg>
"""

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def format_excel_hms(total_minutes):
    """Replica el formato h:mm:ss de Excel incluso para valores negativos."""
    sign = "-" if total_minutes < 0 else ""
    abs_sec = int(round(abs(total_minutes) * 60))
    hours = abs_sec // 3600
    minutes = (abs_sec % 3600) // 60
    seconds = abs_sec % 60
    return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"

# --- LOGO GRANDE CENTRADO ---
logo_b64 = get_base64_image("logo.png")
if logo_b64:
    st.markdown(f"""
    <div class="logo-box">
        <img src="data:image/png;base64,{logo_b64}" style="width: 420px; max-width: 90%; height: auto;" alt="Ingenio Carmelita">
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No se encontró el archivo 'logo.png' en el repositorio.")

# --- BANNER SUPERIOR CON CAÑITAS ---
st.markdown(f"""
<div class="header-banner">
    <div>{SVG_CANITAS}</div>
    <div class="header-text">
        <h1>DISPONIBILIDAD DE TRASLADO</h1>
        <p>Modelo Operativo de Cosecha y Transporte • Ingenio Carmelita</p>
    </div>
    <div>{SVG_CANITAS}</div>
</div>
""", unsafe_allow_html=True)

# --- DISTRIBUCIÓN PRINCIPAL EN 2 COLUMNAS ---
col_izq, col_der = st.columns([1, 1.35], gap="large")

with col_izq:
    # Bloque 1: Datos Manuales
    st.markdown('<div class="sec-header-info">📋 1. Datos Generales del Traslado</div>', unsafe_allow_html=True)
    with st.container(border=True):
        hacienda_inicial = st.text_input("Hacienda inicial", placeholder="Ej. Hacienda La Primavera")
        hacienda_final = st.text_input("Hacienda final", placeholder="Ej. Hacienda El Rosario")
        frente = st.text_input("Frente", placeholder="Ej. Frente 3")

    st.write("")

    # Bloque 2: Variables Operativas (Encabezados Verdes en Excel)
    st.markdown('<div class="sec-header-verde">🟢 2. Variables Editables (Entradas)</div>', unsafe_allow_html=True)
    with st.container(border=True):
        distancia_km = st.number_input("Distancia traslado (km)", min_value=0.0, value=45.0, step=1.0, format="%.2f")
        despacho_prom = st.number_input("Despacho prom/hora", min_value=0.1, value=75.0, step=1.0, format="%.2f")
        toneladas_disp = st.number_input("Toneladas disponibles", min_value=0.0, value=1200.0, step=10.0, format="%.2f")

    # Control de hora actual (NOW() de Excel)
    colombia_tz = datetime.timezone(datetime.timedelta(hours=-5))
    now = datetime.datetime.now(colombia_tz)
    c_hora, c_btn = st.columns([2, 1])
    with c_hora:
        st.caption(f"🕒 **Hora base de cálculo (NOW):** {now.strftime('%d/%m/%Y %I:%M:%S %p')}")
    with c_btn:
        if st.button("🔄 Actualizar hora"):
            st.rerun()

# --- CÁLCULOS EXACTOS IDÉNTICOS A LA HOJA 2 DEL EXCEL ---
# C15: =B18/B16
horas_cana_disp = toneladas_disp / despacho_prom

# C17: =INT((B14/20)-1) -> En Excel INT redondea hacia abajo (permite -1 si Distancia < 20)
paradas_tecnicas = math.floor((distancia_km / 20.0) - 1.0)

# C19: =B14/20
tiempo_traslado_horas = distancia_km / 20.0

# C13: =((C17*10)/(24*60)) -> en minutos es paradas_tecnicas * 10
tiempo_traslado_min = paradas_tecnicas * 10
tiempo_traslado_hms = format_excel_hms(tiempo_traslado_min)

# D18: =NOW()+(C15-2)/24
hora_final_estimada = now + datetime.timedelta(hours=(horas_cana_disp - 2.0))

# D16: =D18-C19/24-C13
hora_inicio = hora_final_estimada - datetime.timedelta(hours=tiempo_traslado_horas) - datetime.timedelta(minutes=tiempo_traslado_min)

# D14: =D16-1/48 (1/48 de día = 30 minutos)
hora_llegada_apoyo = hora_inicio - datetime.timedelta(minutes=30)

with col_der:
    st.markdown('<div class="sec-header-amarillo">🟡 3. Resultados del Modelo</div>', unsafe_allow_html=True)
    with st.container(border=True):
        # Fila 1 de indicadores
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title-yellow">Tiempo de traslado (minutos)</div>
                <div class="kpi-value">{tiempo_traslado_hms}</div>
                <div class="kpi-sub">Equivalente: {tiempo_traslado_min} min</div>
            </div>
            """, unsafe_allow_html=True)
        with r1_c2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title-yellow">Horas de caña disponibles</div>
                <div class="kpi-value">{horas_cana_disp:.2f}</div>
                <div class="kpi-sub">horas de molienda</div>
            </div>
            """, unsafe_allow_html=True)

        # Fila 2 de indicadores
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title-yellow">Paradas tecnicas</div>
                <div class="kpi-value">{paradas_tecnicas}</div>
                <div class="kpi-sub">paradas programadas</div>
            </div>
            """, unsafe_allow_html=True)
        with r2_c2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title-yellow">Tiempo de traslado horas</div>
                <div class="kpi-value">{tiempo_traslado_horas:.2f}</div>
                <div class="kpi-sub">horas de recorrido</div>
            </div>
            """, unsafe_allow_html=True)

        # Fila 3: Horarios estimados
        t1, t2, t3 = st.columns(3)
        with t1:
            st.markdown(f"""
            <div class="time-card">
                <div class="kpi-title-yellow">Hora llegada apoyo</div>
                <div class="time-value">{hora_llegada_apoyo.strftime('%I:%M %p')}</div>
                <div class="time-date">{hora_llegada_apoyo.strftime('%d/%m/%Y')} ({hora_llegada_apoyo.strftime('%H:%M')})</div>
            </div>
            """, unsafe_allow_html=True)
        with t2:
            st.markdown(f"""
            <div class="time-card">
                <div class="kpi-title-yellow">Hora de inicio</div>
                <div class="time-value">{hora_inicio.strftime('%I:%M %p')}</div>
                <div class="time-date">{hora_inicio.strftime('%d/%m/%Y')} ({hora_inicio.strftime('%H:%M')})</div>
            </div>
            """, unsafe_allow_html=True)
        with t3:
            st.markdown(f"""
            <div class="time-card">
                <div class="kpi-title-yellow">Hora final estimada</div>
                <div class="time-value">{hora_final_estimada.strftime('%I:%M %p')}</div>
                <div class="time-date">{hora_final_estimada.strftime('%d/%m/%Y')} ({hora_final_estimada.strftime('%H:%M')})</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        # Botón para guardar en Google Sheets
        if st.button("📤 Enviar información a Google Sheets"):
            webhook_url = "https://script.google.com/macros/s/AKfycbzyR-uC9KdNR3_Anyd6mwMvvQSqE1vkZEjwxtZdP9xKfiQorVj3i82oFOaS5wxMvk3W/exec"

            row_data = [
                now.strftime('%Y-%m-%d %H:%M:%S'),
                hacienda_inicial,
                hacienda_final,
                frente,
                distancia_km,
                despacho_prom,
                toneladas_disp,
                tiempo_traslado_min,
                round(horas_cana_disp, 2),
                paradas_tecnicas,
                round(tiempo_traslado_horas, 2),
                hora_llegada_apoyo.strftime('%Y-%m-%d %H:%M:%S'),
                hora_inicio.strftime('%Y-%m-%d %H:%M:%S'),
                hora_final_estimada.strftime('%Y-%m-%d %H:%M:%S')
            ]

            with st.spinner("Guardando registro en Google Sheets..."):
                try:
                    payload = json.dumps({"row": row_data}).encode("utf-8")
                    req = urllib.request.Request(
                        webhook_url,
                        data=payload,
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req, timeout=15) as response:
                        if response.status == 200:
                            st.success("¡Registro guardado en Google Sheets correctamente!")
                        else:
                            st.error(f"Error al guardar los datos. Código: {response.status}")
                except Exception as e:
                    st.error(f"Error de conexión con Google Sheets: {e}")
