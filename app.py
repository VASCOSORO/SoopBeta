import streamlit as st
import pandas as pd

# Función para cargar el archivo Excel desde la carpeta raíz
@st.cache_data
def load_data():
    try:
        # Cargar el archivo Excel desde la carpeta raíz
        df = pd.read_excel('1083.xlsx', engine='openpyxl')
        return df
    except FileNotFoundError:
        st.error("El archivo '1083.xlsx' no se encontró en la carpeta raíz.")
        return pd.DataFrame()  # Devolver un DataFrame vacío si no se encuentra el archivo

# Cargar los datos
df = load_data()

# Verificar si los datos fueron cargados correctamente
if not df.empty:
    st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo Excel.")
    
    # Mostrar las primeras 5 filas para verificar si se cargan correctamente
    st.write("Primeras 5 filas de los productos cargados:")
    st.write(df.head())
else:
    st.error("No se cargaron datos. Verificá que el archivo '1083.xlsx' esté en la carpeta correcta.")

# Campo de búsqueda
busqueda = st.text_input("Escribí acá para buscar")  # Campo de texto para la búsqueda

# Verificar si el usuario ha escrito algo y filtrar productos
if busqueda and not df.empty:
    # Hacer una búsqueda básica en la columna de 'Nombre'
    productos_filtrados = df[df['Nombre'].str.contains(busqueda, case=False, na=False)]
    
    if not productos_filtrados.empty:
        st.write(f"Se encontraron {productos_filtrados.shape[0]} productos con el término '{busqueda}'.")
        st.write(productos_filtrados[['Nombre', 'Codigo', 'Precio', 'Stock']])  # Mostrar información clave
    else:
        st.write(f"No se encontraron productos con el término '{busqueda}'.")
