import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Salidas------------------------------------------------------------------------
archivo = "Resumen_Salidas_Cada_15_minutos_Octubre_2026.xlsx"
df = pd.read_excel(archivo, sheet_name="REPORTE SALIDAS", skiprows=6)

df["Codigo_Estacion"] = df["Estacion"].str.extract(r"^\((\d+)\)")
df["Nombre_Estacion"] = df["Estacion"].str.replace(r"^\(\d+\)", "", regex=True)

df["Hora"] = pd.to_datetime(df["Intervalo"].astype(str), format="%H:%M:%S").dt.hour
columnas_dias = [c for c in df.columns if c.startswith("_2026_10_")]

df_est_hora = df.groupby(["Codigo_Estacion", "Hora"], as_index=False)[columnas_dias].sum()

mapa_nombres = df.groupby("Codigo_Estacion")["Nombre_Estacion"].last()


df_modelo = df_est_hora.melt(
    id_vars=["Codigo_Estacion", "Hora"],
    value_vars=columnas_dias,
    var_name="Fecha_Str",
    value_name="Salidas")

df_modelo["Fecha"] = pd.to_datetime(df_modelo["Fecha_Str"].str.lstrip("_"), format="%Y_%m_%d")
df_modelo["Dia_Semana_Num"] = df_modelo["Fecha"].dt.dayofweek  # 0=Lunes ... 6=Domingo
dias_es = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
df_modelo["Dia_Semana"] = df_modelo["Dia_Semana_Num"].map(dias_es)
df_modelo["Es_Fin_Semana"] = (df_modelo["Dia_Semana_Num"] >= 5).astype(int)
df_modelo["Dia_Mes"] = df_modelo["Fecha"].dt.day

df_modelo["Hora_Formato"] = df_modelo["Hora"].astype(str).str.zfill(2) + ":00"

def clasificar_franja(h):
    if 5 <= h <= 8:
        return "Pico Mañana"
    elif 9 <= h <= 15:
        return "Valle"
    elif 16 <= h <= 19:
        return "Pico Tarde"
    else:
        return "Madrugada/Noche"

df_modelo["Franja_Horaria"] = df_modelo["Hora"].apply(clasificar_franja)
df_modelo["Nombre_Estacion"] = df_modelo["Codigo_Estacion"].map(mapa_nombres)

df_modelo = df_modelo.drop(columns=["Fecha_Str"])
# Servicios-----------------------------------------------------------------------
df = pd.read_csv('Servicios_(Rutas_Troncales_y_Zonales).csv')

columnas = [
    'nom_ruta',     # Nombre de la ruta
    'orig_ruta',    # Origen
    'dest_ruta',    # Destino
    'long_ruta',    # Longitud de ruta (km)
    'hor_habil',    # Horario días hábiles
    'hor_sab',      # Horario sábados
    'hor_fest',     # Horario domingos y festivos
    'dias_oper',    # Días operativos
    'tip_bus'       # Tipo de bus
]

cond_origen = df['orig_ruta'].str.contains('portal sur', case=False, na=False)
cond_destino = df['dest_ruta'].str.contains('portal sur', case=False, na=False)
cond_troncal = df['comp_sitp'] == 1

df_servicios = df[(cond_origen | cond_destino) & cond_troncal][columnas].copy()

df_servicios['dias_oper'] = df_servicios['dias_oper'].map({
    1: 'L-V',
    2: 'L-S',
    3: 'L-D/F'
})

df_servicios['tip_bus'] = df_servicios['tip_bus'].map({
    1: 'Articulado',
    2: 'Biarticulado',
    3: 'Padrón',
    4: 'Busetón',
    5: 'Microbús',
    6: 'Dual'
})

#Entradas --------------------------------------------------------------
archivo_entradas = "10 TM Resumen de Validaciones Troncales al 31 de Octubre del 2026 Intervalo 15 Mint.xlsx"
df_entradas = pd.read_excel(archivo_entradas, sheet_name="Validaciones Tullave", skiprows=6)

df_entradas = df_entradas[
    df_entradas["Estación"].notna() & (df_entradas["Estación"] != "Total general")
].copy()

df_entradas["Codigo_Estacion"] = df_entradas["Estación"].str.extract(r"^\((\d+)\)")
df_entradas["Nombre_Estacion"] = df_entradas["Estación"].str.replace(r"^\(\d+\)\s*", "", regex=True)

df_entradas["Hora"] = pd.to_datetime(df_entradas["Intervalo"].astype(str), format="%H:%M:%S").dt.hour

columnas_dias = [
    c for c in df_entradas.columns 
    if isinstance(c, pd.Timestamp) or str(c).startswith("2026-10-")
]

df_ent_hora = df_entradas.groupby(["Codigo_Estacion", "Hora"], as_index=False)[columnas_dias].sum()
mapa_nombres_ent = df_entradas.groupby("Codigo_Estacion")["Nombre_Estacion"].last()

df_modelo_entradas = df_ent_hora.melt(
    id_vars=["Codigo_Estacion", "Hora"],
    value_vars=columnas_dias,
    var_name="Fecha_Raw",
    value_name="Entradas"
)

df_modelo_entradas["Fecha"] = pd.to_datetime(df_modelo_entradas["Fecha_Raw"])
df_modelo_entradas["Dia_Semana_Num"] = df_modelo_entradas["Fecha"].dt.dayofweek
dias_es = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
df_modelo_entradas["Dia_Semana"] = df_modelo_entradas["Dia_Semana_Num"].map(dias_es)
df_modelo_entradas["Es_Fin_Semana"] = (df_modelo_entradas["Dia_Semana_Num"] >= 5).astype(int)
df_modelo_entradas["Dia_Mes"] = df_modelo_entradas["Fecha"].dt.day

df_modelo_entradas["Hora_Formato"] = df_modelo_entradas["Hora"].astype(str).str.zfill(2) + ":00"

def clasificar_franja(h):
    if 5 <= h <= 8:
        return "Pico Mañana"
    elif 9 <= h <= 15:
        return "Valle"
    elif 16 <= h <= 19:
        return "Pico Tarde"
    else:
        return "Madrugada/Noche"

df_modelo_entradas["Franja_Horaria"] = df_modelo_entradas["Hora"].apply(clasificar_franja)
df_modelo_entradas["Nombre_Estacion"] = df_modelo_entradas["Codigo_Estacion"].map(mapa_nombres_ent)

df_modelo_entradas = df_modelo_entradas.drop(columns=["Fecha_Raw"])

#Por alcance
estaciones_estudio = [
    # Linea_E
    "07101",  # La Castellana (CASTELLANA)
    "07102",  # NQS Calle 75
    "07103",  # Avenida Chile (AV. CHILE)
    "07104",  # 7 de Agosto
    "07105",  # TIGO (MOVISTAR ARENA)
    "07106",  # Campin - UAN (EL CAMPIN)
    "07107",  # Universidad Nacional (U. NACIONAL)
    "07108",  # Av. Eldorado (Av. El Dorado)
    "07109",  # CAD
    "07110",  # Paloquemao (PALOQUEMAO)
    "07111",  # Ricaurte (NQS - RICAURTE)
    "07200",  # Tygua-San José
    "07201",  # Guatoque - Veraguas (Guatoque -Veraguas)

    # Linea_G (NQS Sur)
    "07000",  # Portal Sur - JFK Coop. Financiera (Portal Sur JFK Coop. Financiera)
    "07001",  # Perdomo (PERDOMO)
    "07002",  # C.C Paseo Villa Del Rio - Madelena (MADELENA)
    "07003",  # Sevillana (SEVILLANA)
    "07004",  # Venecia (VENECIA)
    "07005",  # Alquería (ALQUERIA)
    "07006",  # General Santander
    "07007",  # CL 38A Sur - Centro Mayor (Cl38A sur - CENTRO MAYOR)
    "07008",  # NQS Calle 30 SUR (NQS - Calle 30 Sur)
    "07010",  # Bosa
    "07112",  # Comuneros (COMUNEROS)
    "07113",  # Santa Isabel (SANTA ISABEL)
    "07503",  # San Mateo (SAN MATEO - C.C. UNISUR)
    "07504",  # Terreros - H. Cardiovascular (TERREROS)
    "07505",  # León XIII (LEON XIII)
    "07506",  # La Despensa (DESPENSA)
]
filtro_salidas = (
    df_modelo["Codigo_Estacion"].isin(estaciones_estudio) &
    df_modelo["Hora"].between(3, 22))
filtro_entradas = (
    df_modelo_entradas["Codigo_Estacion"].isin(estaciones_estudio) &
    df_modelo_entradas["Hora"].between(3, 22))
df_estudio_salidas = df_modelo[filtro_salidas].copy()
df_estudio_entradas = df_modelo_entradas[filtro_entradas].copy()

#csv---------------------
df_modelo_entradas.to_csv('entradas_estaciones.csv', index=False, encoding='utf-8-sig')
df_modelo.to_csv('salidas_estaciones.csv', index=False, encoding='utf-8-sig')
#Solo de Linea G y E
df_servicios.to_csv('servicios_portal_sur.csv', index=False, encoding='utf-8-sig')
df_estudio_salidas.to_csv("salidas_estudio.csv", index=False, encoding="utf-8-sig")
df_estudio_entradas.to_csv("entradas_estudio.csv", index=False, encoding="utf-8-sig")

# Graficas --------------------

orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

df_sistema_dia_hora = (
    df_modelo_entradas[df_modelo_entradas["Hora"].between(3, 22)]
    .groupby(["Fecha", "Dia_Semana", "Hora"], as_index=False)["Entradas"]
    .sum()
)

pivot_sistema = (
    df_sistema_dia_hora.pivot_table(index="Hora", columns="Dia_Semana", values="Entradas", aggfunc="mean")
    .reindex(columns=orden_dias)
    .fillna(0)
)

plt.figure(figsize=(10, 7))
sns.heatmap(
    pivot_sistema / 1000,
    cmap="YlGnBu",
    annot=True,
    fmt=".1f",
    cbar_kws={"label": "Promedio Entradas Sistema (Miles / Hora)"}
)
plt.title("Todas las Estaciones - Promedio Entradas por Día y Hora (en Miles)", fontweight="bold")
plt.xlabel("Día de la Semana")
plt.ylabel("Hora del Día")
plt.tight_layout()
plt.show()


top_estacion = (
    df_estudio_entradas.groupby(["Codigo_Estacion", "Nombre_Estacion"])["Entradas"]
    .sum()
    .idxmax()
)
cod_top, nom_top = top_estacion

pivot_top_entradas = (
    df_estudio_entradas[df_estudio_entradas["Codigo_Estacion"] == cod_top]
    .pivot_table(index="Hora", columns="Dia_Semana", values="Entradas", aggfunc="mean")
    .reindex(columns=orden_dias)
    .fillna(0)
)

pivot_top_salidas = (
    df_estudio_salidas[df_estudio_salidas["Codigo_Estacion"] == cod_top]
    .pivot_table(index="Hora", columns="Dia_Semana", values="Salidas", aggfunc="mean")
    .reindex(columns=orden_dias)
    .fillna(0)
)

fig, axes = plt.subplots(1, 2, figsize=(18, 8))

sns.heatmap(
    pivot_top_entradas,
    cmap="YlOrRd",
    annot=True,
    fmt=".0f",
    cbar_kws={"label": "Promedio Entradas / Hora"},
    ax=axes[0]
)
axes[0].set_title(f"Entradas - ({cod_top}) {nom_top}", fontweight="bold")
axes[0].set_xlabel("Día de la Semana")
axes[0].set_ylabel("Hora del Día")

sns.heatmap(
    pivot_top_salidas,
    cmap="YlGnBu",
    annot=True,
    fmt=".0f",
    cbar_kws={"label": "Promedio Salidas / Hora"},
    ax=axes[1]
)
axes[1].set_title(f"Salidas - ({cod_top}) {nom_top}", fontweight="bold")
axes[1].set_xlabel("Día de la Semana")
axes[1].set_ylabel("Hora del Día")

plt.suptitle(f"Comportamiento Horario: ({cod_top}) {nom_top}", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.show()

