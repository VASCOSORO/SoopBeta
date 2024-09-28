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

# Función para limpiar y normalizar los nombres de productos
def limpiar_nombre_producto(nombre):
    if pd.isna(nombre):
        return ""
    return nombre.strip().lower()

# Limpiar los nombres de productos en el DataFrame
df['Nombre Limpio'] = df['Nombre'].apply(limpiar_nombre_producto)

# Campo de búsqueda
busqueda = st.text_input("Escribí acá para buscar")  # Usamos text_input en vez de selectbox

# Verificar si el usuario ha escrito algo y filtrar productos
if busqueda:
    busqueda_limpia = busqueda.strip().lower()  # Limpiamos y normalizamos la búsqueda
    productos_filtrados = df[df['Nombre Limpio'].str.contains(busqueda_limpia, case=False, na=False)]
    
    if not productos_filtrados.empty:
        st.write(f"Se encontraron {productos_filtrados.shape[0]} productos con el término '{busqueda}'.")
        st.write(productos_filtrados[['Nombre', 'Codigo', 'Precio', 'Stock']])  # Mostrar información clave
    else:
        st.write(f"No se encontraron productos con el término '{busqueda}'.")
