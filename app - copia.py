import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración inicial para Streamlit
st.title("Análisis de Clientes - Creación y Asignación")

# Subir archivo Excel
uploaded_file = st.file_uploader("Subí tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Leer el archivo Excel
    df = pd.read_excel(uploaded_file)

    # Asegurarse que las fechas están en formato de fecha
    df['Fecha Creado'] = pd.to_datetime(df['Fecha Creado'], errors='coerce')

    # 1. Gráfico de clientes creados por mes/año
    def grafico_creados_por_mes(df, year=None):
        df['Mes Creado'] = df['Fecha Creado'].dt.to_period('M')  # Agregamos una columna con el mes
        if year:
            df = df[df['Fecha Creado'].dt.year == year]  # Filtramos por el año
        clientes_por_mes = df['Mes Creado'].value_counts().sort_index()

        # Crear el gráfico
        plt.figure(figsize=(10, 6))
        clientes_por_mes.plot(kind='bar')
        plt.title(f'Clientes creados por mes en {year if year else "todos los años"}')
        plt.xlabel('Mes')
        plt.ylabel('Cantidad de clientes')
        plt.xticks(rotation=45)
        st.pyplot(plt)

    # 2. Gráfico de clientes por vendedor
    def grafico_clientes_por_vendedor(df):
        df['Vendedores_principal'] = df['Vendedores'].apply(lambda x: x.split(',')[0].strip() if pd.notna(x) else 'Sin vendedor')  # Primer vendedor como principal
        clientes_por_vendedor = df['Vendedores_principal'].value_counts()

        # Crear el gráfico
        plt.figure(figsize=(12, 6))
        clientes_por_vendedor.plot(kind='bar')
        plt.title('Clientes por Vendedor Principal')
        plt.xlabel('Vendedor')
        plt.ylabel('Cantidad de clientes')
        plt.xticks(rotation=45)
        st.pyplot(plt)

    # 3. Gráfico de clientes sin vendedor
    def grafico_clientes_sin_vendedor(df):
        sin_vendedor = df[df['Vendedores_principal'] == 'Sin vendedor'].shape[0]
        con_vendedor = df[df['Vendedores_principal'] != 'Sin vendedor'].shape[0]

        # Crear el gráfico
        plt.figure(figsize=(6, 6))
        plt.pie([con_vendedor, sin_vendedor], labels=['Con Vendedor', 'Sin Vendedor'], autopct='%1.1f%%', startangle=90)
        plt.title('Clientes con y sin Vendedor')
        st.pyplot(plt)

    # Interfaz para elegir el año
    year = st.number_input("Elegí el año para ver cuántos clientes fueron creados", min_value=2000, max_value=2100, step=1, value=2023)

    # Mostrar los gráficos
    st.subheader("Clientes creados por mes")
    grafico_creados_por_mes(df, year=year)  # Filtrar por el año seleccionado

    st.subheader("Clientes por Vendedor Principal")
    grafico_clientes_por_vendedor(df)

    st.subheader("Clientes con y sin Vendedor")
    grafico_clientes_sin_vendedor(df)
