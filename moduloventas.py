import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import requests
from PIL import Image

# Configuración de la página
st.set_page_config(
    page_title="📁 Modulo Productos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título de la aplicación
st.title("📁 Modulo Productos")

# Función para convertir DataFrame a Excel en memoria usando openpyxl
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Productos')
    excel_bytes = buffer.getvalue()
    return excel_bytes

# Sidebar para cargar el archivo Excel
st.sidebar.header("Cargar Archivo Excel de Productos")
uploaded_file = st.sidebar.file_uploader("📤 Subir archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file, engine='openpyxl')

        # Mostrar los nombres de las columnas para depuración
        st.sidebar.write("🔍 **Columnas en el archivo:**")
        st.sidebar.write(df.columns.tolist())

        # Inicialización de la variable df_modificado
        df_modificado = df.copy()

        # Opciones de filtrado y búsqueda
        st.sidebar.header("Filtrar Productos")
        
        # Buscador de productos
        st.subheader("Buscar y seleccionar producto")
        nombre_buscado = st.text_input("Buscar producto", value="", placeholder="Escribí el nombre del producto...")

        # Filtrar productos que coincidan con el texto buscado usando la columna 'Nombre'
        productos_filtrados = df[df['Nombre'].str.contains(nombre_buscado, case=False, na=False)]

        # Agregar un valor vacío al principio del desplegable
        opciones = [""] + productos_filtrados['Nombre'].tolist()

        # Seleccionar un producto desde el desplegable filtrado
        producto_seleccionado = st.selectbox("Selecciona el producto", opciones)

        # Mostrar detalles del producto seleccionado
        if producto_seleccionado:
            producto = df_modificado[df_modificado['Nombre'] == producto_seleccionado].iloc[0]

            st.subheader(f"Detalles del producto: {producto_seleccionado}")
            
            # Mostrar detalles en columnas
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**ID:** {producto['Id']}")
                st.markdown(f"**Código:** {producto['Codigo']}")
                st.markdown(f"**Nombre:** {producto['Nombre']}")
                st.markdown(f"**Precio:** {producto['Precio']}")
                st.markdown(f"**Precio x Mayor:** {producto['Precio x Mayor']}")
                st.markdown(f"**Descripción:** {producto['Descripcion']}")
                st.markdown(f"**Categorías:** {producto['Categorias']}")

            with col2:
                # Mostrar el stock
                stock_actual = producto['Stock']
                if stock_actual > 10:
                    st.markdown(f"🟢 **Stock: {stock_actual} unidades**")
                elif stock_actual > 0:
                    st.markdown(f"🟡 **Stock: {stock_actual} unidades**")
                else:
                    st.markdown(f"🔴 **Sin stock**")
                
                # Mostrar imagen del producto
                if pd.notnull(producto['imagen']) and producto['imagen'] != '':
                    try:
                        response = requests.get(producto['imagen'], timeout=5)
                        response.raise_for_status()
                        image = Image.open(BytesIO(response.content))
                        st.image(image, width=150)
                    except Exception as e:
                        st.write("🔗 **Imagen no disponible o URL inválida.**")
                else:
                    st.write("🔗 **No hay imagen disponible.**")

        # Opción para descargar la base de datos modificada
        excel = convertir_a_excel(df_modificado)
        st.download_button(
            label="📥 Descargar Excel Modificado",
            data=excel,
            file_name="productos_modificados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("📂 Por favor, sube un archivo Excel para comenzar.")
