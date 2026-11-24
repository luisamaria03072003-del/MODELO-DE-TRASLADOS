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
    page_icon="🚜",
    layout="wide"
)

# --- ESTILOS CSS COMPACTOS PARA PANTALLA COMPLETA DE PC ---
st.markdown("""<style>
.block-container {
    padding-top: 1.0rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 1.6rem !important;
    padding-right: 1.6rem !important;
    max-width: 1400px;
}
header[data-testid="stHeader"] {
    height: 2.0rem;
    background: transparent;
}
.stApp {
    background-color: #F3F6F1;
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0.4rem;
}
.header-banner {
    background: linear-gradient(135deg, #14452F 0%, #246A3E 58%, #388E3C 100%);
    padding: 10px 22px;
    border-radius: 14px;
    color: white;
    box-shadow: 0 4px 14px rgba(20, 69, 47, 0.20);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    border-bottom: 4px solid #FBC02D;
}
.header-logo-wrap {
    background-color: #FFFFFF;
    padding: 6px 14px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.14);
    flex-shrink: 0;
}
.header-text {
    flex: 1;
    text-align: left;
}
.header-text h1 {
    color: #FFFFFF;
    font-size: 1.52rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.15;
    letter-spacing: 0.4px;
}
.header-text p {
    color: #E8F5E9;
    font-size: 0.86rem;
    margin: 3px 0 0 0;
    font-weight: 500;
}
.header-deco {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-header-info {
    background-color: #1B5E20;
    color: #FFFFFF;
    padding: 6px 12px;
    border-radius: 8px 8px 0 0;
    font-weight: 700;
    font-size: 0.9rem;
}
.sec-header-verde {
    background-color: #2E7D32;
    color: #FFFFFF;
    padding: 6px 12px;
    border-radius: 8px 8px 0 0;
    font-weight: 700;
    font-size: 0.9rem;
    border-bottom: 2px solid #A5D6A7;
}
.sec-header-amarillo {
    background-color: #FFF176;
    color: #1F2937;
    padding: 6px 12px;
    border-radius: 8px 8px 0 0;
    font-weight: 800;
    font-size: 0.9rem;
    border-bottom: 2px solid #FBC02D;
}
div[data-testid="stWidgetLabel"] p {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    margin-bottom: 1px !important;
}
.kpi-card {
    background-color: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    overflow: hidden;
    margin-bottom: 6px;
    text-align: center;
}
.kpi-title-yellow {
    background-color: #FFFF66;
    color: #111827;
    font-weight: 700;
    font-size: 0.81rem;
    padding: 5px 8px;
    border-bottom: 1px solid #E6E600;
}
.kpi-value {
    font-size: 1.32rem;
    font-weight: 800;
    color: #14452F;
    padding: 7px 8px 1px 8px;
    line-height: 1.2;
}
.kpi-sub {
    font-size: 0.73rem;
    color: #6B7280;
    padding-bottom: 6px;
}
.time-card {
    background-color: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    overflow: hidden;
    text-align: center;
    margin-bottom: 6px;
}
.time-value {
    font-size: 1.12rem;
    font-weight: 800;
    color: #111827;
    padding: 7px 6px 2px 6px;
    line-height: 1.2;
}
.time-date {
    font-size: 0.75rem;
    font-weight: 600;
    color: #2E7D32;
    padding-bottom: 6px;
}
div.stButton > button {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
    color: white;
    font-weight: 700;
    font-size: 0.92rem;
    padding: 0.42rem 0.9rem;
    border-radius: 8px;
    border: none;
    width: 100%;
    box-shadow: 0 3px 8px rgba(27, 94, 32, 0.22);
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #14452F 0%, #1B5E20 100%);
    color: #FFFF66;
}
.machinery-footer {
    margin-top: 6px;
    padding: 5px 16px;
    background: linear-gradient(90deg, rgba(20,69,47,0.06) 0%, rgba(46,125,50,0.12) 50%, rgba(20,69,47,0.06) 100%);
    border-radius: 10px;
    border-bottom: 2px solid #81C784;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.footer-label {
    font-size: 0.8rem;
    color: #1B5E20;
    font-weight: 700;
}
</style>""", unsafe_allow_html=True)

# --- ILUSTRACIONES VECTORIALES EN UNA SOLA LÍNEA ---
SVG_TRACTOR_HEADER = '<svg width="96" height="58" viewBox="0 0 130 78" fill="none" xmlns="http://www.w3.org/2000/svg"><ellipse cx="66" cy="72" rx="56" ry="3.5" fill="#0D3322" fill-opacity="0.35"/><rect x="6" y="34" width="42" height="24" rx="3" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.8"/><line x1="16" y1="34" x2="16" y2="58" stroke="#2E7D32" stroke-width="1.5"/><line x1="27" y1="34" x2="27" y2="58" stroke="#2E7D32" stroke-width="1.5"/><line x1="38" y1="34" x2="38" y2="58" stroke="#2E7D32" stroke-width="1.5"/><path d="M9 34 Q18 24 28 31 Q37 23 46 34 Z" fill="#DCE775"/><line x1="48" y1="54" x2="58" y2="54" stroke="#E8F5E9" stroke-width="2.5"/><circle cx="17" cy="62" r="7.5" fill="#263238" stroke="#E8F5E9" stroke-width="1.5"/><circle cx="17" cy="62" r="3" fill="#FBC02D"/><circle cx="37" cy="62" r="7.5" fill="#263238" stroke="#E8F5E9" stroke-width="1.5"/><circle cx="37" cy="62" r="3" fill="#FBC02D"/><path d="M62 20 H83 L87 38 H60 Z" fill="#E8F5E9" stroke="#1B5E20" stroke-width="1.8"/><rect x="65" y="23" width="15" height="12" rx="1.5" fill="#81C784"/><rect x="59" y="16" width="27" height="4" rx="2" fill="#FBC02D"/><path d="M85 35 H111 C114 35 116 37 116 40 V52 H85 Z" fill="#FBC02D" stroke="#1B5E20" stroke-width="1.6"/><path d="M96 35 V23 L100 20" stroke="#E8F5E9" stroke-width="2.4" stroke-linecap="round"/><circle cx="71" cy="56" r="14" fill="#263238" stroke="#E8F5E9" stroke-width="2"/><circle cx="71" cy="56" r="6" fill="#FBC02D"/><circle cx="107" cy="60" r="9.5" fill="#263238" stroke="#E8F5E9" stroke-width="1.8"/><circle cx="107" cy="60" r="4" fill="#FBC02D"/></svg>'

SVG_CANITAS_COMPACT = '<svg width="46" height="56" viewBox="0 0 90 110" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M32 38 C14 28, 6 34, 4 44 C14 38, 24 38, 32 43 Z" fill="#A5D6A7"/><path d="M32 62 C12 54, 4 62, 2 72 C13 64, 23 64, 32 68 Z" fill="#81C784"/><rect x="30" y="14" width="9" height="86" rx="4" fill="#C5E1A5" stroke="#558B2F" stroke-width="1.5"/><line x1="30" y1="34" x2="39" y2="34" stroke="#33691E" stroke-width="2.5"/><line x1="30" y1="56" x2="39" y2="56" stroke="#33691E" stroke-width="2.5"/><line x1="30" y1="78" x2="39" y2="78" stroke="#33691E" stroke-width="2.5"/><path d="M34 16 C26 4, 16 4, 10 10 C19 9, 27 12, 33 19 Z" fill="#AED581"/><path d="M54 12 C64 2, 76 3, 82 10 C72 8, 63 10, 55 16 Z" fill="#AED581"/><path d="M56 44 C74 34, 84 40, 86 50 C76 44, 66 44, 56 49 Z" fill="#A5D6A7"/><path d="M56 70 C76 62, 84 70, 86 80 C75 72, 65 72, 56 76 Z" fill="#81C784"/><rect x="48" y="8" width="10" height="92" rx="4.5" fill="#DCE775" stroke="#689F38" stroke-width="1.5"/><line x1="48" y1="28" x2="58" y2="28" stroke="#33691E" stroke-width="2.5"/><line x1="48" y1="50" x2="58" y2="50" stroke="#33691E" stroke-width="2.5"/><line x1="48" y1="72" x2="58" y2="72" stroke="#33691E" stroke-width="2.5"/></svg>'

SVG_COSECHADORA_MINI = '<svg width="86" height="32" viewBox="0 0 140 52" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="34" y="16" width="54" height="22" rx="4" fill="#2E7D32"/><path d="M66 6 H84 L88 18 H64 Z" fill="#66BB6A"/><path d="M36 22 L12 8 L16 5 L40 18 Z" fill="#1B5E20"/><path d="M88 24 L112 36 L112 43 L88 38 Z" fill="#FBC02D"/><rect x="40" y="37" width="42" height="10" rx="5" fill="#1F2937"/><circle cx="46" cy="42" r="3" fill="#FBC02D"/><circle cx="61" cy="42" r="3" fill="#FBC02D"/><circle cx="76" cy="42" r="3" fill="#FBC02D"/></svg>'

SVG_CAMABAJA_MINI = '<svg width="110" height="32" viewBox="0 0 180 52" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M128 16 H150 L158 28 V40 H128 Z" fill="#1B5E20"/><rect x="136" y="19" width="12" height="9" rx="1.5" fill="#A5D6A7"/><path d="M14 38 H108 L118 30 H128 V36 L114 42 H14 Z" fill="#374151"/><rect x="44" y="20" width="32" height="13" rx="2.5" fill="#FBC02D"/><rect x="48" y="11" width="14" height="10" rx="1.5" fill="#2E7D32"/><circle cx="52" cy="34" r="6" fill="#1F2937"/><circle cx="71" cy="35" r="4.5" fill="#1F2937"/><circle cx="24" cy="44" r="5" fill="#111827"/><circle cx="37" cy="44" r="5" fill="#111827"/><circle cx="122" cy="44" r="5" fill="#111827"/><circle cx="148" cy="44" r="5" fill="#111827"/></svg>'

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def fmt_excel_hms(days_val):
    """Formatea una fracción de día exactamente como h:mm:ss en Excel."""
    total_sec = int(round(days_val * 86400))
    sign = "-" if total_sec < 0 else ""
    s = abs(total_sec)
    hours = s // 3600
    minutes = (s % 3600) // 60
    seconds = s % 60
    return f"{sign}{hours}:{minutes:02d}:{seconds:02d}"

# --- ENCABEZADO CON LOGO + TÍTULO + TRACTOR Y CAÑITAS ---
logo_b64 = get_base64_image("logo.png")
logo_html = f'<div class="header-logo-wrap"><img src="data:image/png;base64,{logo_b64}" style="height: 58px; width: auto;" alt="Ingenio Carmelita"></div>' if logo_b64 else ""

st.markdown(f'<div class="header-banner">{logo_html}<div class="header-text"><h1>DISPONIBILIDAD TRASLADO DE MAQUINARIA</h1><p>Logística de Maquinaria Agrícola, Cosecha y Transporte • Ingenio Carmelita</p></div><div class="header-deco">{SVG_TRACTOR_HEADER}{SVG_CANITAS_COMPACT}</div></div>', unsafe_allow_html=True)

# --- DISTRIBUCIÓN PRINCIPAL EN 2 COLUMNAS COMPACTAS ---
col_izq, col_der = st.columns([1.05, 1.35], gap="medium")

with col_izq:
    st.markdown('<div class="sec-header-info">📋 1. Información General</div>', unsafe_allow_html=True)
    with st.container(border=True):
        c_h1, c_h2, c_h3 = st.columns(3)
        with c_h1:
            hacienda_inicial = st.text_input("Hacienda inicial", placeholder="Ej. Primavera")
        with c_h2:
            hacienda_final = st.text_input("Hacienda final", placeholder="Ej. El Rosario")
        with c_h3:
            frente = st.text_input("Frente", placeholder="Ej. Frente 3")

    st.markdown('<div class="sec-header-verde">🟢 2. Variables Editables</div>', unsafe_allow_html=True)
    with st.container(border=True):
        v1, v2 = st.columns(2)
        with v1:
            distancia_km = st.number_input("Distancia traslado (km)", min_value=0.0, value=60.0, step=1.0, format="%.2f")
        with v2:
            despacho_prom = st.number_input("Despacho prom/hora", min_value=0.1, value=100.0, step=1.0, format="%.2f")
        toneladas_disp = st.number_input("Toneladas disponibles", min_value=0.0, value=300.0, step=10.0, format="%.2f")

    colombia_tz = datetime.timezone(datetime.timedelta(hours=-5))
    now_live = datetime.datetime.now(colombia_tz)

    usar_hora_manual = st.checkbox("Fijar hora base manualmente (para comparar exacto con Excel)", value=False)
    if usar_hora_manual:
        c_d, c_t = st.columns(2)
        with c_d:
            fecha_manual = st.date_input("Fecha base", value=now_live.date())
        with c_t:
            hora_manual = st.time_input("Hora base (NOW)", value=now_live.time().replace(second=0, microsecond=0))
        now = datetime.datetime.combine(fecha_manual, hora_manual, tzinfo=colombia_tz)
    else:
        now = now_live
        c_hora, c_btn = st.columns([2.2, 1])
        with c_hora:
            st.caption(f"🕒 **Hora actual (NOW):** {now.strftime('%d/%m/%Y %I:%M %p')}")
        with c_btn:
            if st.button("🔄 Actualizar"):
                st.rerun()

# --- CÁLCULOS EXACTOS DEL MODELO ---
# 1. Paradas tecnicas: 1 parada cada 20 km sin contar la llegada (<=20 km -> 0, 37 km -> 1, 60 km -> 2)
paradas_tecnicas = max(0, math.ceil(round(distancia_km / 20.0, 9)) - 1)

# 2. Tiempo de parada técnica (C13): =((C17*10)/(24*60)) [en días, formato h:mm:ss]
tiempo_parada_dias = (paradas_tecnicas * 10.0) / (24.0 * 60.0)
tiempo_parada_hms = fmt_excel_hms(tiempo_parada_dias)

# 3. Horas de caña disponibles (C15): =(B18/B16)/24 [en días, formato h:mm:ss]
horas_cana_num = toneladas_disp / despacho_prom
horas_cana_dias = horas_cana_num / 24.0
horas_cana_hms = fmt_excel_hms(horas_cana_dias)

# 4. Tiempo de traslado horas (C19): =(B14/20)/24 + C13 [en días, formato h:mm:ss]
tiempo_traslado_dias = ((distancia_km / 20.0) / 24.0) + tiempo_parada_dias
tiempo_traslado_hms = fmt_excel_hms(tiempo_traslado_dias)

# 5. Hora final estimada (D18): =NOW() + (C15*24 - 2)/24
hora_final_estimada = now + datetime.timedelta(days=(horas_cana_dias * 24.0 - 2.0) / 24.0)

# 6. Hora de inicio (D16): =D18 - C19
hora_inicio = hora_final_estimada - datetime.timedelta(days=tiempo_traslado_dias)

# 7. Hora llegada apoyo (D14): =D16 - 1/48
hora_llegada_apoyo = hora_inicio - datetime.timedelta(days=1.0 / 48.0)

with col_der:
    st.markdown('<div class="sec-header-amarillo">🟡 3. Resultados del Modelo</div>', unsafe_allow_html=True)
    with st.container(border=True):
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title-yellow">Tiempo de parada tecnica</div><div class="kpi-value">{tiempo_parada_hms}</div><div class="kpi-sub">Formato Excel h:mm:ss ({paradas_tecnicas * 10} min)</div></div>', unsafe_allow_html=True)
        with r1_c2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title-yellow">Horas de caña disponibles</div><div class="kpi-value">{horas_cana_hms}</div><div class="kpi-sub">Formato Excel h:mm:ss ({horas_cana_num:.2f} h)</div></div>', unsafe_allow_html=True)

        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title-yellow">Paradas tecnicas</div><div class="kpi-value">{paradas_tecnicas}</div><div class="kpi-sub">REDONDEAR.MAS(Distancia/20; 0) - 1</div></div>', unsafe_allow_html=True)
        with r2_c2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title-yellow">Tiempo de traslados horas</div><div class="kpi-value">{tiempo_traslado_hms}</div><div class="kpi-sub">Recorrido + paradas (h:mm:ss)</div></div>', unsafe_allow_html=True)

        t1, t2, t3 = st.columns(3)
        with t1:
            st.markdown(f'<div class="time-card"><div class="kpi-title-yellow">Hora de llegada de apoyo</div><div class="time-value">{hora_llegada_apoyo.strftime("%H:%M")}</div><div class="time-date">{hora_llegada_apoyo.strftime("%d/%m/%Y %H:%M")} ({hora_llegada_apoyo.strftime("%I:%M %p")})</div></div>', unsafe_allow_html=True)
        with t2:
            st.markdown(f'<div class="time-card"><div class="kpi-title-yellow">Hora de inicio</div><div class="time-value">{hora_inicio.strftime("%H:%M")}</div><div class="time-date">{hora_inicio.strftime("%d/%m/%Y %H:%M")} ({hora_inicio.strftime("%I:%M %p")})</div></div>', unsafe_allow_html=True)
        with t3:
            st.markdown(f'<div class="time-card"><div class="kpi-title-yellow">Hora final estimada</div><div class="time-value">{hora_final_estimada.strftime("%H:%M")}</div><div class="time-date">{hora_final_estimada.strftime("%d/%m/%Y %H:%M")} ({hora_final_estimada.strftime("%I:%M %p")})</div></div>', unsafe_allow_html=True)

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
                tiempo_parada_hms,
                horas_cana_hms,
                paradas_tecnicas,
                tiempo_traslado_hms,
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

# --- FRANJA DECORATIVA SUTIL DE MAQUINARIA AGRÍCOLA ---
st.markdown(f'<div class="machinery-footer">{SVG_COSECHADORA_MINI}<span class="footer-label">🌿 Traslado de Equipos y Cosechadoras • Ingenio Carmelita S.A.</span>{SVG_CAMABAJA_MINI}</div>', unsafe_allow_html=True)
