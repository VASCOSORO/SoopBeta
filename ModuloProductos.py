import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz
import os

# Configuración de la página
st.set_page_config(
    page_title="📁 Módulo Productos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Definir las columnas esperadas globalmente
columnas_esperadas = [
    'Código', 'Código de Barras', 'Nombre', 'Descripción',
    'Alto', 'Ancho', 'Categorias', 'Proveedor',
    'Costo (Pesos)', 'Costo (USD)', 'Último Precio (Pesos)',
    'Último Precio (USD)', 'Precio x Mayor', 'Precio',
    'Precio x Menor', 'Precio Promocional x Mayor',
    'Precio Promocional', 'Precio Promocional x Menor',
    'Pasillo', 'Estante', 'Columna', 'Fecha de Vencimiento',
    'Nota 1', 'Activo'
]

# Función para cargar proveedores desde ProveedoresSoop.xlsx
def cargar_proveedores():
    proveedores_path = 'ProveedoresSoop.xlsx'
    if os.path.exists(proveedores_path):
        try:
            proveedores_df = pd.read_excel(proveedores_path, engine='openpyxl')
            if 'Proveedor' in proveedores_df.columns:
                proveedores = proveedores_df['Proveedor'].dropna().unique().tolist()
                return proveedores
            else:
                st.sidebar.warning("⚠️ La columna 'Proveedor' no se encontró en 'ProveedoresSoop.xlsx'.")
                return []
        except Exception as e:
            st.sidebar.error(f"❌ Error al leer 'ProveedoresSoop.xlsx': {e}")
            return []
    else:
        st.sidebar.warning("⚠️ El archivo 'ProveedoresSoop.xlsx' no se encontró. Por favor, agrégalo desde el módulo correspondiente.")
        return []

# Sidebar para cargar el archivo CSV o Excel
st.sidebar.header("📅 Cargar Archivo de Productos")
uploaded_file = st.sidebar.file_uploader("📄 Subir archivo CSV o Excel", type=["csv", "xlsx"])

# Cargar proveedores
proveedores = cargar_proveedores()

# Inicializar el DataFrame en session_state para mantener los cambios
if 'df_productos' not in st.session_state:
    st.session_state.df_productos = pd.DataFrame(columns=columnas_esperadas)

# Leer el archivo subido y actualizar el DataFrame en session_state
if uploaded_file is not None:
    try:
        st.write("📂 **Leyendo archivo...**")
        # Detectar el tipo de archivo subido y leerlo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', sep=None, engine='python', on_bad_lines='skip')
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')

        # Asegurarse de que todas las columnas esperadas existan
        for col in columnas_esperadas:
            if col not in df.columns:
                df[col] = ''

        # Reordenar las columnas según `columnas_esperadas`
        df = df[columnas_esperadas]

        # Asignar al session_state
        st.session_state.df_productos = df
        st.success("✅ Archivo cargado correctamente.")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al leer el archivo: {e}")

# Mostrar el buscador para buscar un producto para editar
if not st.session_state.df_productos.empty:
    st.subheader("🔍 Buscar Producto para Editar")
    # Crear una opción para buscar por Nombre o Código
    search_option = st.radio("Buscar por:", options=["Nombre", "Código"], horizontal=True)

    if search_option == "Nombre":
        buscar_producto = st.selectbox("Selecciona el Nombre del Producto", options=[''] + st.session_state.df_productos['Nombre'].dropna().unique().tolist())
    else:
        buscar_producto = st.selectbox("Selecciona el Código del Producto", options=[''] + st.session_state.df_productos['Código'].dropna().astype(str).unique().tolist())
else:
    buscar_producto = ''

# Variable para almacenar si se seleccionó un producto
producto_seleccionado = None
if buscar_producto:
    try:
        if search_option == "Nombre":
            producto_seleccionado = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == buscar_producto].iloc[0]
        else:
            producto_seleccionado = st.session_state.df_productos[st.session_state.df_productos['Código'].astype(str) == buscar_producto].iloc[0]
        st.write(f"**Producto Seleccionado: {producto_seleccionado['Nombre']}**")
    except Exception as e:
        st.error(f"❌ Error al seleccionar el producto: {e}")

# Formulario para agregar o editar productos
st.subheader("➕ Agregar/Editar Producto")
with st.form(key='agregar_producto_unique'):
    nuevo_codigo = st.text_input("Código", value=str(producto_seleccionado['Código']) if producto_seleccionado is not None else "")
    nuevo_nombre = st.text_input("Nombre", value=producto_seleccionado['Nombre'] if producto_seleccionado is not None else "")
    nuevo_costo_pesos = st.number_input("Costo (Pesos)", min_value=0.0, step=0.01, value=float(producto_seleccionado['Costo (Pesos)']) if producto_seleccionado is not None and pd.notna(producto_seleccionado['Costo (Pesos)']) else 0.0)

    # Agregar el botón de envío del formulario
    guardar = st.form_submit_button(label='Guardar Producto')

    if guardar:
        if not nuevo_codigo or not nuevo_nombre:
            st.error("❌ Por favor, completa los campos obligatorios (Código y Nombre).")
        else:
            st.success("✅ Producto guardado correctamente.")

# Agregar el footer
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #555;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
    }
    </style>
    <div class="footer">
        Powered by VASCO.SORO
    </div>
    """, unsafe_allow_html=True)
