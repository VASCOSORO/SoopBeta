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

# Función para cargar archivo Produt2.csv y convertir a Produt2.xlsx
def cargar_y_convertir_csv():
    csv_path = 'Produt2.csv'
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, encoding='ISO-8859-1', sep=None, engine='python', on_bad_lines='skip')
            # Asegurarse de que todas las columnas esperadas existan
            for col in columnas_esperadas:
                if col not in df.columns:
                    df[col] = ''
            # Reordenar las columnas según `columnas_esperadas`
            df = df[columnas_esperadas]
            # Guardar como Excel
            df.to_excel('Produt2.xlsx', index=False, engine='openpyxl')
            st.success("✅ Archivo 'Produt2.csv' convertido y guardado como 'Produt2.xlsx'.")
        except Exception as e:
            st.error(f"❌ Error al convertir 'Produt2.csv': {e}")
    else:
        st.warning("⚠️ El archivo 'Produt2.csv' no se encontró en la carpeta raíz.")

# Sidebar para cargar el archivo CSV y convertirlo a Excel
st.sidebar.header("📥 Cargar y Convertir Archivo de Productos")
if st.sidebar.button("Cargar 'Produt2.csv' y Convertir a Excel"):
    cargar_y_convertir_csv()

# Inicializar el DataFrame en session_state para mantener los cambios
if 'df_productos' not in st.session_state:
    if os.path.exists('Produt2.xlsx'):
        try:
            st.session_state.df_productos = pd.read_excel('Produt2.xlsx', engine='openpyxl')
        except Exception as e:
            st.session_state.df_productos = pd.DataFrame(columns=columnas_esperadas)
            st.error(f"❌ Error al leer 'Produt2.xlsx': {e}")
    else:
        st.session_state.df_productos = pd.DataFrame(columns=columnas_esperadas)

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
    nuevo_costo_pesos = st.number_input("Costo (Pesos)", min_value=0.0, step=0.01, value=float(producto_seleccionado['Costo (Pesos)']) if producto_seleccionado is not None and pd.notna(producto_seleccionado['Costo (Pesos)']) and producto_seleccionado['Costo (Pesos)'] != '' else 0.0)

    # Agregar el botón de envío del formulario
    guardar = st.form_submit_button(label='Guardar Producto')

    if guardar:
        if not nuevo_codigo or not nuevo_nombre:
            st.error("❌ Por favor, completa los campos obligatorios (Código y Nombre).")
        else:
            # Actualizar o agregar el producto en el DataFrame
            if producto_seleccionado is not None:
                idx = st.session_state.df_productos.index[st.session_state.df_productos['Código'] == producto_seleccionado['Código']].tolist()[0]
                st.session_state.df_productos.loc[idx, 'Código'] = nuevo_codigo
                st.session_state.df_productos.loc[idx, 'Nombre'] = nuevo_nombre
                st.session_state.df_productos.loc[idx, 'Costo (Pesos)'] = nuevo_costo_pesos
                st.success("✅ Producto actualizado correctamente.")
            else:
                nuevo_producto = {
                    'Código': nuevo_codigo,
                    'Nombre': nuevo_nombre,
                    'Costo (Pesos)': nuevo_costo_pesos,
                    # Agregar el resto de las columnas con valores predeterminados
                }
                st.session_state.df_productos = pd.concat([st.session_state.df_productos, pd.DataFrame([nuevo_producto])], ignore_index=True)
                st.success("✅ Producto agregado correctamente.")

            # Guardar los cambios en el archivo Excel
            try:
                st.session_state.df_productos.to_excel('Produt2.xlsx', index=False, engine='openpyxl')
                st.success("✅ Cambios guardados en 'Produt2.xlsx'.")
            except Exception as e:
                st.error(f"❌ Error al guardar los cambios en 'Produt2.xlsx': {e}")

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
