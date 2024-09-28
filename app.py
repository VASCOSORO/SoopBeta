import streamlit as st
import pandas as pd
import requests

# Función para descargar el archivo desde GitHub y cargarlo en pandas
@st.cache_data
def load_data_from_github():
    try:
        # URL cruda del archivo Excel en tu repositorio de GitHub
        url = "https://raw.githubusercontent.com/VASCOSORO/tu_repositorio/main/1083.xlsx"
        
        # Descargar el archivo Excel
        response = requests.get(url)
        
        # Guardar el contenido del archivo descargado en un archivo temporal
        with open('1083.xlsx', 'wb') as f:
            f.write(response.content)
        
        # Cargar el archivo Excel
        df = pd.read_excel('1083.xlsx', engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

# Botón para recargar los datos
if st.button('Recargar archivo desde GitHub'):
    st.cache_data.clear()  # Limpiar la caché

# Cargar los datos
df = load_data_from_github()

# Verificar si los datos fueron cargados correctamente
if not df.empty:
    st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo Excel.")
    
    # Mostrar las primeras 5 filas para verificar si se cargan correctamente
    st.write("Primeras 5 filas de los productos cargados:")
    st.write(df.head())
else:
    st.error("No se cargaron datos. Verificá que el archivo '1083.xlsx' esté en el repositorio de GitHub.")

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
