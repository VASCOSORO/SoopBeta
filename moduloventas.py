import streamlit as st
import pandas as pd
from io import BytesIO

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

        # Mostrar los nombres de las columnas
        st.write("🔍 **Columnas en el archivo cargado:**")
        columnas = df.columns.tolist()
        st.write(columnas)  # Muestra la lista de columnas

        # Verificar si existe la columna 'Producto' o 'Nombre'
        if 'Producto' in columnas or 'Nombre' in columnas:
            # Definir la columna correcta para filtrar
            columna_producto = 'Producto' if 'Producto' in columnas else 'Nombre'
            st.write(f"Usando la columna '{columna_producto}' para buscar productos.")

            # Mostrar los primeros valores de la columna
            st.write(df[columna_producto].head())

            # Inicialización de la variable df_modificado
            df_modificado = df.copy()

            # Buscador de productos
            st.subheader("Buscar y seleccionar producto")
            nombre_buscado = st.text_input("Buscar producto", value="", placeholder="Escribí el nombre del producto...")

            # Filtrar productos que coincidan con el texto buscado usando la columna seleccionada
            productos_filtrados = df[df[columna_producto].str.contains(nombre_buscado, case=False, na=False)]

            # Agregar un valor vacío al principio del desplegable
            opciones = [""] + productos_filtrados[columna_producto].tolist()

            # Seleccionar un producto desde el desplegable filtrado
            producto_seleccionado = st.selectbox("Selecciona el producto", opciones)

            # Mostrar detalles del producto seleccionado
            if producto_seleccionado:
                producto = df_modificado[df_modificado[columna_producto] == producto_seleccionado].iloc[0]

                st.subheader(f"Detalles del producto: {producto_seleccionado}")
                
                # Mostrar detalles en columnas
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**ID:** {producto['Id']}")
                    st.markdown(f"**Código:** {producto['Codigo']}")
                    st.markdown(f"**Nombre:** {producto[columna_producto]}")
                    st.markdown(f"**Precio:** {producto['Precio']}")
                    st.markdown(f"**Precio x Mayor:** {producto['Precio x Mayor']}")
                    st.markdown(f"**Descripción:** {producto['Descripcion']}")
                    st.markdown(f"**Categorías:** {producto['Categorias']}")
                
        else:
            st.error("La columna 'Producto' o 'Nombre' no existe en el archivo. Verifica el archivo Excel.")
            st.stop()

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
