#Creamos el archivo de la APP en el interprete principal 
#####################################################
#Importamos librerias
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
######################################################
#Configuración general de la página 
st.set_page_config(page_title="Dashboard GAC", layout="wide")
######################################################
#PALETA DE COLORES: vino tinto, borgoña y blanco
Paleta_Vino = ['#4A0414', '#800020', '#9B1B30', '#B03A48', '#C9747F', '#DDA0A8', '#6D2E46', '#EFD3D7']
Escala_Vino = ['#FFFFFF', '#EFD3D7', '#C9747F', '#9B1B30', '#4A0414']
######################################################
#DISEÑO: colores del título, barra lateral y tarjetas KPI
st.markdown("""
<style>
h1 {color: #800020;}
h3 {color: #9B1B30;}
[data-testid="stSidebar"] {background-color: #F5E6E8;}
[data-testid="stSidebar"] h1 {color: #4A0414;}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {color: #4A0414 !important;}
[data-testid="stMetric"] {background-color: #F7ECEE; border-left: 6px solid #800020;
                          padding: 10px; border-radius: 8px;}
[data-testid="stMetric"] * {color: #4A0414;}
</style>
""", unsafe_allow_html=True)
######################################################
#Definimos la instancia
@st.cache_resource
######################################################
#Creamos la función de carga de datos
def load_data():
   #Lectura de las bases ya limpias 
   df_bitacora = pd.read_csv("Bitacora_Piso_Limpia.csv", parse_dates=['Fecha'])
   df_leads = pd.read_csv("Leads_Reales_Limpia.csv")
   #Variables para el análisis univariado
   Lista_Bitacora = ['Asesor', 'Prueba_Manejo']
   Lista_Leads = ['Nivel_Efectividad']
   return df_bitacora, df_leads, Lista_Bitacora, Lista_Leads
###############################################################################
#Cargar los datos obtenidos 
df_bitacora, df_leads, Lista_Bitacora, Lista_Leads = load_data()
###############################################################################
#CREACIÓN DEL DASHBOARD
##############################################################################
#Generamos los encabezados para la barra lateral
st.sidebar.title("GAC · Leads y Piso")
#Widget 1: Selectbox
#Menu desplegable para elegir la base de datos
View = st.sidebar.selectbox(label="Base de datos", options=["Bitácora de Piso", "Leads Reales"])
st.sidebar.markdown("---")

##############################################################################
# CONTENIDO DE LA VISTA 1: BITÁCORA DE PISO
if View == "Bitácora de Piso":
    #Widget 2: Selectbox de variables
    Variable_Cat = st.sidebar.selectbox(label="Variables", options=Lista_Bitacora)
    #Widget 3: Multiselect para filtrar meses, ordenados de forma cronológica
    Orden_Meses = df_bitacora.sort_values('Mes_Num')['Mes'].unique().tolist()
    Meses_Sel = st.sidebar.multiselect(label="Filtrar por mes", options=Orden_Meses, default=Orden_Meses)

    #Filtramos la base con los meses seleccionados
    df_filtro = df_bitacora[df_bitacora['Mes'].isin(Meses_Sel)]
    if df_filtro.empty:
        st.warning("Selecciona al menos un mes en la barra lateral.")
        st.stop()

    #Obtenemos las frecuencias de las categorías de la variable seleccionada
    Tabla_frecuencias = df_filtro[Variable_Cat].value_counts().reset_index()
    #Ajustamos los nombre de las cabeceras de las columnas
    Tabla_frecuencias.columns = ['categorias', 'frecuencia']
    #Agregamos porcentaje y porcentaje acumulado
    Tabla_frecuencias['porcentaje'] = (Tabla_frecuencias['frecuencia'] / Tabla_frecuencias['frecuencia'].sum() * 100).round(1)
    Tabla_frecuencias['porcentaje_acumulado'] = Tabla_frecuencias['porcentaje'].cumsum().round(1)

    #Encabezados para el dashboard
    st.title("Extracción de Características · Bitácora de Piso")
    st.caption("Etapa I. Modelado explicativo – Análisis univariado de la variable: " + Variable_Cat)

    #KPIs
    KPI_1, KPI_2, KPI_3, KPI_4 = st.columns(4)
    KPI_1.metric(" Visitas registradas", len(df_filtro))
    KPI_2.metric(" Con prueba de manejo", str(round(df_filtro['PDM'].mean() * 100, 1)) + " %")
    KPI_3.metric(" Intervención gerente", str(round(df_filtro['Inter_Gerente'].mean() * 100, 1)) + " %")
    KPI_4.metric(" Ventas cerradas", int(df_filtro['Venta'].sum()))

    #Cuadro de hallazgos
    Top_Categoria = Tabla_frecuencias['categorias'][0]
    Top_Porcentaje = Tabla_frecuencias['porcentaje'][0]
    if Variable_Cat == 'Asesor':
        Top3 = Tabla_frecuencias['porcentaje'].head(3).sum().round(1)
        st.info("**Hallazgo:** " + str(Top_Categoria) + " atiende el " + str(Top_Porcentaje) +
                "% de las visitas y los 3 asesores principales concentran el " + str(Top3) +
                "% del piso. La carga no está distribuida de forma equitativa.")
    else:
        Porcentaje_Si = Tabla_frecuencias[Tabla_frecuencias['categorias'] == 'Sí']['porcentaje'].sum()
        st.info("**Hallazgo:** solo el " + str(Porcentaje_Si) +
                "% de las visitas realiza prueba de manejo; la mayoría de los clientes de piso se va sin probar el vehículo, "
                "lo que frena el avance hacia solicitud de crédito y venta.")

    #Generamos el diseño del Layout deseado
    # Fila 1
    Contenedor_A, Contenedor_B = st.columns(2)
    with Contenedor_A:
        st.write("Grafico de Barras")
        #GRAPH 1: BARPLOT
        figure1 = px.bar(data_frame=Tabla_frecuencias, x='categorias', y='frecuencia',
                         title='Frecuencia por categoría', color='frecuencia', text='frecuencia',
                         color_continuous_scale=Escala_Vino)
        figure1.update_xaxes(automargin=True)
        figure1.update_yaxes(automargin=True)
        figure1.update_layout(height=320)
        st.plotly_chart(figure1, use_container_width=True)

    with Contenedor_B:
        st.write("Grafico de anillo o dona")
        #GRAPH 2: DONUT PLOT
        figure2 = px.pie(data_frame=Tabla_frecuencias, names='categorias', values='frecuencia',
                         hole=0.45, title='Participación por categoría',
                         color_discrete_sequence=Paleta_Vino)
        figure2.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        figure2.update_layout(height=320)
        st.plotly_chart(figure2, use_container_width=True)

    # Fila 2
    Contenedor_C, Contenedor_D = st.columns(2)
    with Contenedor_C:
        st.write("Grafico de Pareto")
        #GRAPH 3: PARETO 
        figure3 = go.Figure()
        figure3.add_trace(go.Bar(x=Tabla_frecuencias['categorias'], y=Tabla_frecuencias['frecuencia'],
                                 name='Frecuencia', marker_color='#800020'))
        figure3.add_trace(go.Scatter(x=Tabla_frecuencias['categorias'], y=Tabla_frecuencias['porcentaje_acumulado'],
                                     name='% acumulado', yaxis='y2', mode='lines+markers',
                                     line=dict(color='#C9747F', width=3)))
        figure3.update_layout(title='Pareto de frecuencias', height=320,
                              yaxis2=dict(overlaying='y', side='right', range=[0, 105], title='%'),
                              legend=dict(orientation='h', y=-0.25))
        st.plotly_chart(figure3, use_container_width=True)

    with Contenedor_D:
        st.write("Grafico de Treemap")
        #GRAPH 4: TREEMAP
        figure4 = px.treemap(data_frame=Tabla_frecuencias, path=['categorias'], values='frecuencia',
                             color='frecuencia', color_continuous_scale=Escala_Vino,
                             title='Peso de cada categoría')
        figure4.update_layout(height=320)
        st.plotly_chart(figure4, use_container_width=True)

    # Fila 3
    Contenedor_E, Contenedor_F = st.columns(2)
    with Contenedor_E:
        st.write("Heatmap por mes")
        #GRAPH 5: HEATMAP categoría vs mes
        Tabla_cruzada = pd.crosstab(df_filtro[Variable_Cat], df_filtro['Mes'])
        #Ordenamos las columnas de forma cronológica
        Tabla_cruzada = Tabla_cruzada[[mes for mes in Orden_Meses if mes in Tabla_cruzada.columns]]
        figure5 = px.imshow(Tabla_cruzada, text_auto=True, aspect='auto',
                            color_continuous_scale=Escala_Vino, title='Visitas por categoría y mes')
        figure5.update_layout(height=350)
        st.plotly_chart(figure5, use_container_width=True)

    with Contenedor_F:
        st.write("Boxplot de visitas diarias")
        #GRAPH 6: BOXPLOT (distribución de visitas por día en cada categoría)
        Visitas_Dia = df_filtro.groupby(['Fecha', Variable_Cat]).size().reset_index(name='Visitas')
        figure6 = px.box(data_frame=Visitas_Dia, x=Variable_Cat, y='Visitas', color=Variable_Cat,
                         points='all', color_discrete_sequence=Paleta_Vino,
                         title='Visitas por día según categoría')
        figure6.update_layout(height=350, showlegend=False)
        st.plotly_chart(figure6, use_container_width=True)

    # Fila 4
    st.subheader("Tabla de frecuencias")
    st.dataframe(Tabla_frecuencias.style.background_gradient(cmap='Reds', subset=['frecuencia']),
                 use_container_width=True, hide_index=True)

##############################################################################
# CONTENIDO DE LA VISTA 2: LEADS REALES
if View == "Leads Reales":
    #Widget 2: Selectbox de variables
    Variable_Cat = st.sidebar.selectbox(label="Variables", options=Lista_Leads)
    #Widget 3: Multiselect para filtrar años
    Lista_Años = sorted(df_leads['Año'].unique().tolist())
    Años_Sel = st.sidebar.multiselect(label="Filtrar por año", options=Lista_Años, default=Lista_Años)
        #Cambiamos el color del texto del radio (título y opciones) a vino tinto
    st.sidebar.markdown("<style>[data-testid='stSidebar'] [data-testid='stRadio'] * {color: #4A0414;}</style>", unsafe_allow_html=True)
    #Widget 4: Radio para elegir el indicador del heatmap
    Indicador = st.sidebar.radio(label="Indicador del heatmap",
                                 options=['Efectividad_Leads', 'Conversion', 'Total', 'Ventas'])

    #Filtramos la base con los años seleccionados
    df_filtro = df_leads[df_leads['Año'].isin(Años_Sel)]
    if df_filtro.empty:
        st.warning("Selecciona al menos un año en la barra lateral.")
        st.stop()

    #Obtenemos las frecuencias (meses por nivel) en orden Baja - Media - Alta
    Tabla_frecuencias = df_filtro[Variable_Cat].value_counts().reindex(['Baja', 'Media', 'Alta'], fill_value=0).reset_index()
    Tabla_frecuencias.columns = ['categorias', 'frecuencia']
    Tabla_frecuencias['porcentaje'] = (Tabla_frecuencias['frecuencia'] / Tabla_frecuencias['frecuencia'].sum() * 100).round(1)
    #Colores fijos por nivel
    Colores_Nivel = {'Alta': '#4A0414', 'Media': '#9B1B30', 'Baja': '#DDA0A8'}

    #Generamos los encabezados para el dashboard
    st.title("Extracción de Características · Leads Reales")
    st.caption("Etapa I. Modelado explicativo – Análisis univariado de la variable: " + Variable_Cat +
               " (Baja ≤ 55% · Media 55–70% · Alta > 70%)")

    #KPIs
    KPI_1, KPI_2, KPI_3, KPI_4 = st.columns(4)
    KPI_1.metric("Leads totales", f"{int(df_filtro['Total'].sum()):,}")
    KPI_2.metric("Efectividad promedio", str(round(df_filtro['Efectividad_Leads'].mean(), 1)) + " %")
    KPI_3.metric("Conversión promedio", str(round(df_filtro['Conversion'].mean(), 1)) + " %")
    KPI_4.metric("Ventas", int(df_filtro['Ventas'].sum()))

    #Cuadro de hallazgos
    Mejor_Mes = df_filtro.sort_values('Efectividad_Leads', ascending=False).iloc[0]
    Peor_Mes = df_filtro.sort_values('Efectividad_Leads').iloc[0]
    Meses_Baja = Tabla_frecuencias[Tabla_frecuencias['categorias'] == 'Baja']['frecuencia'].sum()
    st.info("**Hallazgo:** " + str(Meses_Baja) + " de " + str(len(df_filtro)) +
            " meses tienen efectividad Baja. Mejor mes: " + Mejor_Mes['Periodo'] + " (" +
            str(Mejor_Mes['Efectividad_Leads']) + "%) · Peor mes: " + Peor_Mes['Periodo'] + " (" +
            str(Peor_Mes['Efectividad_Leads']) + "%).")

    #Generamos el diseño del Layout deseado
    # Fila 1
    Contenedor_A, Contenedor_B = st.columns(2)
    with Contenedor_A:
        st.write("Grafico de Barras")
        #GRAPH 1: BARPLOT
        figure1 = px.bar(data_frame=Tabla_frecuencias, x='categorias', y='frecuencia', text='frecuencia',
                         title='Meses por nivel de efectividad', color='categorias',
                         color_discrete_map=Colores_Nivel)
        figure1.update_layout(height=320, showlegend=False)
        st.plotly_chart(figure1, use_container_width=True)

    with Contenedor_B:
        st.write("Grafico de anillo o dona")
        #GRAPH 2: DONUT PLOT
        figure2 = px.pie(data_frame=Tabla_frecuencias, names='categorias', values='frecuencia', hole=0.45,
                         title='Participación de cada nivel', color='categorias',
                         color_discrete_map=Colores_Nivel)
        figure2.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        figure2.update_layout(height=320)
        st.plotly_chart(figure2, use_container_width=True)

    # Fila 2
    Contenedor_C, Contenedor_D = st.columns(2)
    with Contenedor_C:
        st.write("Heatmap año vs mes")
        #GRAPH 3: HEATMAP del indicador seleccionado
        Orden_Meses = df_leads.sort_values('Mes_Num')['Mes'].unique().tolist()
        Tabla_calor = df_filtro.pivot_table(index='Año', columns='Mes', values=Indicador)
        Tabla_calor = Tabla_calor[[mes for mes in Orden_Meses if mes in Tabla_calor.columns]]
        Tabla_calor.index = Tabla_calor.index.astype(str)
        figure3 = px.imshow(Tabla_calor, text_auto=True, aspect='auto',
                            color_continuous_scale=Escala_Vino, title=Indicador + ' por año y mes')
        figure3.update_layout(height=320)
        st.plotly_chart(figure3, use_container_width=True)

    with Contenedor_D:
        st.write("Boxplot de efectividad")
        #GRAPH 4: BOXPLOT de la variable numérica original por nivel
        figure4 = px.box(data_frame=df_filtro, x='Nivel_Efectividad', y='Efectividad_Leads',
                         color='Nivel_Efectividad', points='all', color_discrete_map=Colores_Nivel,
                         category_orders={'Nivel_Efectividad': ['Baja', 'Media', 'Alta']},
                         title='Distribución de la efectividad (%)')
        figure4.update_layout(height=320, showlegend=False)
        st.plotly_chart(figure4, use_container_width=True)

    # Fila 3
    st.write("Grafico de barras en el tiempo")
    #GRAPH 5: BARRAS POR PERIODO con líneas de corte de cada nivel
    figure5 = px.bar(data_frame=df_filtro, x='Periodo', y='Efectividad_Leads', color='Nivel_Efectividad',
                     color_discrete_map=Colores_Nivel, title='Efectividad de leads por mes',
                     category_orders={'Nivel_Efectividad': ['Baja', 'Media', 'Alta']})
    figure5.add_hline(y=55, line_dash='dash', line_color='#9B1B30', annotation_text='55%')
    figure5.add_hline(y=70, line_dash='dash', line_color='#4A0414', annotation_text='70%')
    figure5.update_layout(height=350)
    st.plotly_chart(figure5, use_container_width=True)

    # Fila 4
    st.subheader("Tabla de frecuencias")
    st.dataframe(Tabla_frecuencias.style.background_gradient(cmap='Reds', subset=['frecuencia']),
                 use_container_width=True, hide_index=True)
###################################################################################
