import streamlit as st
import pandas as pd

# Cargar el archivo Excel
@st.cache_data
def load_data():
    df = pd.read_excel('1083.xlsx', engine='openpyxl')  # Cargar el archivo Excel
    return df

# Cargar datos
df = load_data()

# Verificar el número exacto de filas y columnas cargadas
st.write(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo Excel.")

# Mostrar las primeras 5 filas para verificar si se cargan correctamente
st.write("Primeras 5 filas de los productos cargados:")
st.write(df.head())

# Mostrar cuántos valores nulos hay en cada columna
st.write("Valores nulos por columna:")
st.write(df.isnull().sum())

# Campo de búsqueda
busqueda = st.text_input("Escribí acá para buscar")  # Cambié a text_input para búsquedas más amplias

# Verificar si el usuario ha escrito algo y filtrar productos
if busqueda:
    productos_filtrados = df[df['Nombre'].str.contains(busqueda, case=False, na=False)]  # Incluí 'na=False' para evitar errores si hay valores nulos
    if not productos_filtrados.empty:
        st.write(f"Se encontraron {productos_filtrados.shape[0]} productos con el término '{busqueda}'.")
        st.write(productos_filtrados)
    else:
        st.write(f"No se encontraron productos con el término '{busqueda}'.")
