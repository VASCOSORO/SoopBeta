import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Función para limpiar y convertir a entero eliminando solo puntos
def limpiar_id(valor):
    if pd.isnull(valor):
        return None
    # Eliminar solo puntos
    valor_limpio = str(valor).replace('.', '')
    try:
        return int(valor_limpio)
    except ValueError:
        return None

# Función para procesar y convertir DataFrame a Excel en memoria
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Hoja1')
    buffer.seek(0)
    return buffer

# Interfaz para subir archivos en Streamlit
st.title("Convertidor de CSV para Productos, Clientes y Pedidos")

# Sección para el archivo de Productos
st.header("Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    try:
        # Leer el archivo CSV con separador ';' y codificación 'ISO-8859-1'
        df_productos = pd.read_csv(
            uploaded_file_productos,
            encoding='ISO-8859-1',
            sep=';',
            on_bad_lines='skip',
            dtype=str  # Leer todas las columnas como cadenas para evitar problemas de tipo
        )
        
        # Verificar y limpiar la columna 'Id'
        if 'Id' in df_productos.columns:
            df_productos['Id'] = df_productos['Id'].apply(limpiar_id)
        else:
            st.error("La columna 'Id' no se encuentra en el archivo de Productos.")
        
        # Renombrar las columnas especificadas
        columnas_a_renombrar = {
            'Costo FOB': 'Costo en U$s',  # Cambio de 'Costo FOB' a 'Costo en U$s'
            'Precio jugueteria Face': 'Precio',  # Cambio de 'Precio jugueteria Face' a 'Precio'
            'Precio': 'Precio x Mayor'  # Cambio de 'Precio' a 'Precio x Mayor'
        }
        df_productos = df_productos.rename(columns=columnas_a_renombrar)
        
        # Eliminar columnas que no sirven
        columnas_a_eliminar = ['Precio Face + 50', 'Precio Bonus']
        df_productos = df_productos.drop(columns=columnas_a_eliminar, errors='ignore')
        
        # Agregar nuevas columnas vacías si no existen
        nuevas_columnas = ['Proveedor', 'Pasillo', 'Estante', 'Fecha de Vencimiento']
        for columna in nuevas_columnas:
            if columna not in df_productos.columns:
                df_productos[columna] = ''
        
        # Mostrar una tabla de datos modificada en la interfaz de Streamlit
        st.write("Archivo de Productos modificado:")
        st.dataframe(df_productos)
        
        # Convertir el DataFrame a Excel en memoria
        excel_productos = convertir_a_excel(df_productos)
        
        # Proporcionar un enlace para descargar el archivo
        st.download_button(
            label="Descargar archivo modificado de Productos",
            data=excel_productos,
            file_name="archivo_modificado_productos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo de Productos: {e}")

# Sección para el archivo de Clientes
st.header("Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")

if uploaded_file_clientes is not None:
    try:
        # Leer el archivo CSV con separador ';' y codificación 'ISO-8859-1'
        df_clientes = pd.read_csv(
            uploaded_file_clientes,
            encoding='ISO-8859-1',
            sep=';',
            on_bad_lines='skip',
            dtype=str  # Leer todas las columnas como cadenas para evitar problemas de tipo
        )
        
        # Limpiar y convertir las columnas 'Id' y 'Id Cliente' a entero
        columnas_id = ['Id', 'Id Cliente']
        for columna in columnas_id:
            if columna in df_clientes.columns:
                df_clientes[columna] = df_clientes[columna].apply(limpiar_id)
            else:
                st.warning(f"La columna '{columna}' no se encuentra en el archivo de Clientes.")
        
        # Mostrar una tabla de datos en la interfaz de Streamlit
        st.write("Archivo de Clientes cargado:")
        st.dataframe(df_clientes)
        
        # Convertir el DataFrame a Excel en memoria
        excel_clientes = convertir_a_excel(df_clientes)
        
        # Proporcionar un enlace para descargar el archivo
        st.download_button(
            label="Descargar archivo modificado de Clientes",
            data=excel_clientes,
            file_name="archivo_modificado_clientes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo de Clientes: {e}")

# Sección para el archivo de Pedidos
st.header("Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")

if uploaded_file_pedidos is not None:
    try:
        # Leer el archivo CSV con separador ';' y codificación 'ISO-8859-1'
        df_pedidos = pd.read_csv(
            uploaded_file_pedidos,
            encoding='ISO-8859-1',
            sep=';',
            on_bad_lines='skip',
            dtype=str  # Leer todas las columnas como cadenas para evitar problemas de tipo
        )
        
        # Limpiar y convertir las columnas 'Id' y 'Id Cliente' a entero
        columnas_id = ['Id', 'Id Cliente']
        for columna in columnas_id:
            if columna in df_pedidos.columns:
                df_pedidos[columna] = df_pedidos[columna].apply(limpiar_id)
            else:
                st.warning(f"La columna '{columna}' no se encuentra en el archivo de Pedidos.")
        
        # Mostrar una tabla de datos en la interfaz de Streamlit
        st.write("Archivo de Pedidos cargado:")
        st.dataframe(df_pedidos)
        
        # Convertir el DataFrame a Excel en memoria
        excel_pedidos = convertir_a_excel(df_pedidos)
        
        # Proporcionar un enlace para descargar el archivo
        st.download_button(
            label="Descargar archivo modificado de Pedidos",
            data=excel_pedidos,
            file_name="archivo_modificado_pedidos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo de Pedidos: {e}")
