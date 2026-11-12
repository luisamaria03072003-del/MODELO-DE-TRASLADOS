import math
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

# Constante de velocidad promedio extraída de Modelo.xlsx (50 km / 1.42857 h = 35 km/h)
VELOCIDAD_TRASLADO_KMH = 35.0

# ID de la hoja de cálculo de Google Sheets destino
SPREADSHEET_ID = "1PS6448Q_JvjOXsdXkXbypJcBKQ0VsbeVyBTeKkILSIo"

# Alcances requeridos para autenticar la cuenta de servicio con Google Sheets y Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def formatear_hora_reloj(horas_decimales: float) -> str:
    """Convierte horas decimales al formato horario HH:MM de Excel (ej. 2.4285 -> '02:26')."""
    total_minutos = int(round(horas_decimales * 60)) % (24 * 60)
    hh = total_minutos // 60
    mm = total_minutos % 60
    return f"{hh:02d}:{mm:02d}"


def formatear_numero(valor: float) -> int | float:
    """Mantiene enteros sin decimales cuando aplica y redondea decimales a 2 cifras."""
    redondeado = round(float(valor), 2)
    if redondeado.is_integer():
        return int(redondeado)
    return redondeado


def calcular_modelo_despacho(
    distancia_km: float,
    despacho_promedio_tnh: float,
    tons_disponible_tn: float,
) -> tuple[pd.DataFrame, dict]:
    """
    Replica exactamente las fórmulas y la tabla de 24 horas (01:00 a 00:00) de Modelo.xlsx.
    Retorna el DataFrame completo (incluyendo fila TOTAL) y el diccionario de resumen.
    """
    # Tiempo de traslado en horas (formato original en horas del Excel: Distancia / 35)
    tiempo_traslado_h = distancia_km / VELOCIDAD_TRASLADO_KMH

    num_horas = 24
    horas_reloj = [formatear_hora_reloj(h) for h in range(1, num_horas + 1)]
    tiempo_estimado_llegada = [
        formatear_hora_reloj(h + tiempo_traslado_h) for h in range(1, num_horas + 1)
    ]

    en_proceso_anterior = [0.0] * num_horas
    salidas_anterior = [0.0] * num_horas
    llegando_anterior = [0.0] * num_horas
    faltantes_fabrica = [0.0] * num_horas

    inicio_despacho_nueva = [""] * num_horas
    despachadas_nueva = [0.0] * num_horas
    inicio_llegadas_nueva = [""] * num_horas
    en_proceso_nueva = [0.0] * num_horas
    llegando_nueva = [0.0] * num_horas
    total_llegando_fabrica = [0.0] * num_horas
    meta_programada = [float(despacho_promedio_tnh)] * num_horas
    diferencia_meta = [0.0] * num_horas

    # 1. Cálculo de despachos por hora desde hacienda anterior y hacienda nueva
    cambio_registrado = False
    hora_inicio_despacho_nueva = "N/A"
    hora_inicio_llegadas_nueva = "N/A"

    for i in range(num_horas):
        if i == 0:
            en_proceso_anterior[i] = float(tons_disponible_tn)
        else:
            en_proceso_anterior[i] = max(
                0.0, en_proceso_anterior[i - 1] - salidas_anterior[i - 1]
            )

        salidas_anterior[i] = min(en_proceso_anterior[i], float(despacho_promedio_tnh))
        despachadas_nueva[i] = max(
            0.0, float(despacho_promedio_tnh) - salidas_anterior[i]
        )

        # Marca la primera hora en que la hacienda nueva comienza a despachar
        if despachadas_nueva[i] > 0 and not cambio_registrado:
            inicio_despacho_nueva[i] = horas_reloj[i]
            inicio_llegadas_nueva[i] = tiempo_estimado_llegada[i]
            hora_inicio_despacho_nueva = horas_reloj[i]
            hora_inicio_llegadas_nueva = tiempo_estimado_llegada[i]
            cambio_registrado = True

    # 2. Cálculo de llegadas a fábrica según el tiempo de traslado en horas
    for j in range(num_horas):
        hora_salida = j + 1
        hora_llegada_slot = math.ceil(hora_salida + tiempo_traslado_h - 1e-9)
        if 1 <= hora_llegada_slot <= num_horas:
            idx_llegada = hora_llegada_slot - 1
            llegando_anterior[idx_llegada] += salidas_anterior[j]
            llegando_nueva[idx_llegada] += despachadas_nueva[j]

    # 3. Saldos en proceso, faltantes por llegar y totales en fábrica
    for i in range(num_horas):
        if i == 0:
            faltantes_fabrica[i] = max(
                0.0, float(tons_disponible_tn) - llegando_anterior[i]
            )
            en_proceso_nueva[i] = despachadas_nueva[i] - llegando_nueva[i]
        else:
            faltantes_fabrica[i] = max(
                0.0, faltantes_fabrica[i - 1] - llegando_anterior[i]
            )
            en_proceso_nueva[i] = (
                en_proceso_nueva[i - 1] + despachadas_nueva[i] - llegando_nueva[i]
            )

        total_llegando_fabrica[i] = llegando_anterior[i] + llegando_nueva[i]
        diferencia_meta[i] = total_llegando_fabrica[i] - meta_programada[i]

    # Construcción del DataFrame con las columnas exactas de Modelo.xlsx
    filas = []
    for i in range(num_horas):
        filas.append(
            {
                "HORA": horas_reloj[i],
                "TONELADAS EN PROCESO HACIENDA ANTERIOR": formatear_numero(
                    en_proceso_anterior[i]
                ),
                "TONS SALIDAS": formatear_numero(salidas_anterior[i]),
                "TONS QUE VAN LLEGANDO": formatear_numero(llegando_anterior[i]),
                "TN FALTANTES POR LLEGADA A FABRICA": formatear_numero(
                    faltantes_fabrica[i]
                ),
                "TIEMPO ESTIMADO DE LLEGADA": tiempo_estimado_llegada[i],
                "INICIO DE DESPACHO HDA NUEVA": inicio_despacho_nueva[i],
                "TONS DESPACHADAS HDA NUEVA": formatear_numero(despachadas_nueva[i]),
                "INICIO LLEGADAS HDA NUEVA": inicio_llegadas_nueva[i],
                "TONS EN PROCESO HDA NUEVA": formatear_numero(en_proceso_nueva[i]),
                "TONS QUE VAN LLEGANDO HDA NUEVA": formatear_numero(llegando_nueva[i]),
                "TN TOTAL QUE VAN LLEGANDO FABRICA": formatear_numero(
                    total_llegando_fabrica[i]
                ),
                "DESPACHO PROMEDIO (TN/H)": formatear_numero(meta_programada[i]),
                "DIFERENCIA": formatear_numero(diferencia_meta[i]),
            }
        )

    # Fila de totales igual a la fila final de Modelo.xlsx
    fila_total = {
        "HORA": "TOTAL",
        "TONELADAS EN PROCESO HACIENDA ANTERIOR": "",
        "TONS SALIDAS": formatear_numero(sum(salidas_anterior)),
        "TONS QUE VAN LLEGANDO": formatear_numero(sum(llegando_anterior)),
        "TN FALTANTES POR LLEGADA A FABRICA": "",
        "TIEMPO ESTIMADO DE LLEGADA": "",
        "INICIO DE DESPACHO HDA NUEVA": "",
        "TONS DESPACHADAS HDA NUEVA": formatear_numero(sum(despachadas_nueva)),
        "INICIO LLEGADAS HDA NUEVA": "",
        "TONS EN PROCESO HDA NUEVA": "",
        "TONS QUE VAN LLEGANDO HDA NUEVA": formatear_numero(sum(llegando_nueva)),
        "TN TOTAL QUE VAN LLEGANDO FABRICA": formatear_numero(
            sum(total_llegando_fabrica)
        ),
        "DESPACHO PROMEDIO (TN/H)": formatear_numero(sum(meta_programada)),
        "DIFERENCIA": formatear_numero(sum(diferencia_meta)),
    }

    df_resultado = pd.DataFrame(filas + [fila_total])

    resumen = {
        "tiempo_traslado_h": round(tiempo_traslado_h, 1),
        "inicio_despacho_nueva": hora_inicio_despacho_nueva,
        "inicio_llegadas_nueva": hora_inicio_llegadas_nueva,
        "total_llegadas_fabrica": formatear_numero(sum(total_llegando_fabrica)),
        "total_programado": formatear_numero(sum(meta_programada)),
        "diferencia_total": formatear_numero(sum(diferencia_meta)),
    }

    return df_resultado, resumen


def enviar_a_google_sheets(datos_fila: dict) -> None:
    """Conecta con Google Sheets mediante cuenta de servicio en st.secrets y agrega la fila."""
    credenciales_info = dict(st.secrets["gcp_service_account"])
    credenciales = Credentials.from_service_account_info(
        credenciales_info, scopes=SCOPES
    )
    cliente = gspread.authorize(credenciales)
    hoja = cliente.open_by_key(SPREADSHEET_ID).sheet1

    # Si la hoja está vacía, inserta primero los encabezados
    if len(hoja.get_all_values()) == 0:
        hoja.append_row(list(datos_fila.keys()), value_input_option="USER_ENTERED")

    hoja.append_row(list(datos_fila.values()), value_input_option="USER_ENTERED")


def main() -> None:
    st.set_page_config(
        page_title="Cambio de Hacienda - Modelo de Despacho",
        layout="wide",
    )

    st.title("Cambio de Hacienda — Modelo de Despacho y Traslado")

    # Sección de entrada de haciendas y parámetros del modelo (valores base de Modelo.xlsx)
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        hacienda_inicio = st.text_input("Hacienda de inicio", value="")
    with col_h2:
        hacienda_final = st.text_input("Hacienda final", value="")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        distancia_km = st.number_input(
            "Distancia del traslado (KM)",
            min_value=0.0,
            value=50.0,
            step=1.0,
        )
    with col_p2:
        despacho_promedio_tnh = st.number_input(
            "Despacho promedio por hora (TN/H)",
            min_value=0.0,
            value=19.0,
            step=1.0,
        )
    with col_p3:
        tons_disponible_tn = st.number_input(
            "Toneladas disponibles (TN)",
            min_value=0.0,
            value=98.0,
            step=1.0,
        )

    # Recálculo automático al modificar cualquiera de los parámetros
    df_modelo, resumen = calcular_modelo_despacho(
        distancia_km=distancia_km,
        despacho_promedio_tnh=despacho_promedio_tnh,
        tons_disponible_tn=tons_disponible_tn,
    )

    # Indicadores principales conservando unidades originales (H, HH:MM, TN)
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tiempo de traslado (H)", f"{resumen['tiempo_traslado_h']} H")
    m2.metric("Inicio despacho Hda. Nueva", resumen["inicio_despacho_nueva"])
    m3.metric("Inicio llegadas Hda. Nueva", resumen["inicio_llegadas_nueva"])
    m4.metric(
        "Total llegadas a fábrica (TN)",
        f"{resumen['total_llegadas_fabrica']} TN",
        delta=f"{resumen['diferencia_total']} TN vs meta",
    )

    # Tabla completa del modelo de 24 horas
    st.subheader("Detalle Horario del Cambio de Hacienda")
    st.dataframe(df_modelo, use_container_width=True, hide_index=True)

    # Gráfico de comportamiento de llegadas a fábrica (replicando el gráfico de Modelo.xlsx)
    st.subheader("Comportamiento de Llegadas a Fábrica (TN/H)")
    df_grafico = df_modelo.iloc[:-1].set_index("HORA")[
        ["TN TOTAL QUE VAN LLEGANDO FABRICA", "DESPACHO PROMEDIO (TN/H)"]
    ]
    st.line_chart(df_grafico)

    # Envío de parámetros y haciendas a Google Sheets
    st.divider()
    if st.button("Enviar datos a Google Sheets", type="primary"):
        registro = {
            "Hacienda de Inicio": hacienda_inicio,
            "Hacienda Final": hacienda_final,
            "Distancia del Traslado (KM)": formatear_numero(distancia_km),
            "Tiempo de Traslado (H)": resumen["tiempo_traslado_h"],
            "Despacho Promedio (TN/H)": formatear_numero(despacho_promedio_tnh),
            "Tons Disponible (TN)": formatear_numero(tons_disponible_tn),
            "Inicio Despacho Hda Nueva": resumen["inicio_despacho_nueva"],
            "Inicio Llegadas Hda Nueva": resumen["inicio_llegadas_nueva"],
            "Total Llegadas Fabrica (TN)": resumen["total_llegadas_fabrica"],
        }
        try:
            enviar_a_google_sheets(registro)
            st.success("Datos enviados correctamente a Google Sheets.")
        except Exception as error:
            st.error(f"Error al enviar los datos a Google Sheets: {error}")


if __name__ == "__main__":
    main()