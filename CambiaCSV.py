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

# Función para procesar archivos (Productos, Clientes, Pedidos)
def procesar_archivo(
    uploaded_file,
    tipo,
    columnas_a_renombrar,
    columnas_a_eliminar,
    columnas_a_agregar,
    columnas_id
):
    if uploaded_file is not None:
        try:
            # Leer el archivo CSV con separador ';' y codificación 'ISO-8859-1'
            df = pd.read_csv(
                uploaded_file,
                encoding='ISO-8859-1',
                sep=';',
                on_bad_lines='skip',
                dtype=str  # Leer todas las columnas como cadenas para evitar problemas de tipo
            )
            
            # Limpiar y convertir las columnas de identificación a entero
            for columna in columnas_id:
                if columna in df.columns:
                    df[columna] = df[columna].apply(limpiar_id)
                else:
                    st.warning(f"La columna '{columna}' no se encuentra en el archivo de {tipo}.")
            
            # Renombrar las columnas especificadas
            df = df.rename(columns=columnas_a_renombrar)
            
            # Eliminar columnas que no sirven
            df = df.drop(columns=columnas_a_eliminar, errors='ignore')
            
            # Agregar nuevas columnas vacías si no existen
            for columna in columnas_a_agregar:
                if columna not in df.columns:
                    df[columna] = ''
            
            # Opcional: Convertir las columnas 'Id' a cadenas para evitar formato con comas en Streamlit
            for columna in columnas_id:
                if columna in df.columns:
                    df[columna] = df[columna].astype('Int64').astype(str)
            
            # Mostrar una tabla de datos modificada en la interfaz de Streamlit
            st.write(f"Archivo de {tipo} modificado:")
            st.dataframe(df)
            
            # Convertir el DataFrame a Excel en memoria
            excel = convertir_a_excel(df)
            
            # Proporcionar un enlace para descargar el archivo
            st.download_button(
                label=f"Descargar archivo modificado de {tipo}",
                data=excel,
                file_name=f"archivo_modificado_{tipo.lower()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Ocurrió un error al procesar el archivo de {tipo}: {e}")

# Sección para el archivo de Productos
st.header("Convertidor para CSV de Productos")
uploaded_file_productos = st.file_uploader("Subí tu archivo CSV de Productos", type=["csv"], key="productos")

if uploaded_file_productos is not None:
    columnas_a_renombrar = {
        'Costo FOB': 'Costo en U$s',  # Cambio de 'Costo FOB' a 'Costo en U$s'
        'Precio jugueterias face': 'Precio',  # Cambio de 'Precio jugueterias face' a 'Precio'
        'Precio': 'Precio x Mayor'  # Cambio de 'Precio' a 'Precio x Mayor'
    }
    columnas_a_eliminar = ['Precio Face + 50', 'Precio Bonus']
    columnas_a_agregar = ['Proveedor', 'Pasillo', 'Estante', 'Fecha de Vencimiento']
    columnas_id = ['Id']
    
    procesar_archivo(
        uploaded_file=uploaded_file_productos,
        tipo="Productos",
        columnas_a_renombrar=columnas_a_renombrar,
        columnas_a_eliminar=columnas_a_eliminar,
        columnas_a_agregar=columnas_a_agregar,
        columnas_id=columnas_id
    )

# Sección para el archivo de Clientes
st.header("Convertidor para CSV de Clientes")
uploaded_file_clientes = st.file_uploader("Subí tu archivo CSV de Clientes", type=["csv"], key="clientes_file")

if uploaded_file_clientes is not None:
    columnas_a_renombrar = {}  # No se especifica renombrado para Clientes
    columnas_a_eliminar = []  # No se especifica eliminación para Clientes
    columnas_a_agregar = []  # No se especifica nuevas columnas para Clientes
    columnas_id = ['Id', 'Id Cliente']
    
    procesar_archivo(
        uploaded_file=uploaded_file_clientes,
        tipo="Clientes",
        columnas_a_renombrar=columnas_a_renombrar,
        columnas_a_eliminar=columnas_a_eliminar,
        columnas_a_agregar=columnas_a_agregar,
        columnas_id=columnas_id
    )

# Sección para el archivo de Pedidos
st.header("Convertidor para CSV de Pedidos")
uploaded_file_pedidos = st.file_uploader("Subí tu archivo CSV de Pedidos", type=["csv"], key="pedidos_file")

if uploaded_file_pedidos is not None:
    columnas_a_renombrar = {}  # No se especifica renombrado para Pedidos
    columnas_a_eliminar = []  # No se especifica eliminación para Pedidos
    columnas_a_agregar = []  # No se especifica nuevas columnas para Pedidos
    columnas_id = ['Id', 'Id Cliente']
    
    procesar_archivo(
        uploaded_file=uploaded_file_pedidos,
        tipo="Pedidos",
        columnas_a_renombrar=columnas_a_renombrar,
        columnas_a_eliminar=columnas_a_eliminar,
        columnas_a_agregar=columnas_a_agregar,
        columnas_id=columnas_id
    )
