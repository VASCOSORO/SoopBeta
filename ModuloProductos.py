# ===== Modulo Productos 2.0 para Carga ======
# ================
# =============

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz
import os

st.set_page_config(
    page_title="📁 Módulo Productos",
    layout="wide",
    initial_sidebar_state="expanded",
)

columnas_esperadas = [
    'id', 'id externo', 'Codigo', 'Codigo de Barras', 'Nombre', 'Descripcion',
    'Alto', 'Ancho', 'Categorias', 'Proveedor',
    'Costo (Pesos)', 'Costo (USD)', 'Ultimo Precio (Pesos)',
    'Ultimo Precio (USD)', 'Precio x Mayor', 'Precio Venta',
    'Precio x Menor', 'Precio Promocional x Mayor',
    'Precio Promocional', 'Precio Promocional x Menor',
    'Pasillo', 'Estante', 'Columna', 'Fecha de Vencimiento',
    'Nota 1', 'Activo', 'Imagen', 'Unidades por Bulto', 'Venta Forzada', 'Presentacion'
]

def cargar_excel():
    excel_path = 'Produt2.xlsx'
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            st.success("✅ **Archivo Excel leído correctamente.**")

            columnas_actuales = df.columns.str.strip().str.lower()
            mapeo_columnas = {
                'precio jugueterias face': 'Precio Venta',
                'precio': 'Precio x Mayor',
                'costo fob': 'Costo (USD)',
                'costo': 'Costo (Pesos)',
                'id': 'id',
                'id externo': 'id externo'
            }

            for col_actual, col_esperada in mapeo_columnas.items():
                if col_actual in columnas_actuales:
                    df.rename(columns={df.columns[columnas_actuales.get_loc(col_actual)]: col_esperada}, inplace=True)

            for col in columnas_esperadas:
                if col not in df.columns:
                    df[col] = ''

            df = df[columnas_esperadas]

            df['Ultima Actualizacion'] = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%Y-%m-%d %H:%M:%S")

            df.to_excel('Produt2.xlsx', index=False, engine='openpyxl')
            st.success("✅ Archivo 'Produt2.xlsx' actualizado con éxito.")

            st.write("### Vista Previa de los Datos Convertidos:")
            st.dataframe(df.head(10))

            return df
        except Exception as e:
            st.error(f"❌ Error al leer 'Produt2.xlsx': {e}")
    else:
        st.warning("⚠️ El archivo 'Produt2.xlsx' no se encontró en la carpeta raíz.")
    return None

if 'df_productos' not in st.session_state:
    df_convertido = cargar_excel()
    if df_convertido is not None:
        st.session_state.df_productos = df_convertido
    else:
        st.session_state.df_productos = pd.DataFrame(columns=columnas_esperadas)

if not st.session_state.df_productos.empty:
    st.subheader("🔍 Buscar Producto para Editar")
    col_search1, col_search2 = st.columns(2)
    with col_search1:
        buscar_codigo = st.selectbox(
            "Buscar por Código",
            options=[''] + st.session_state.df_productos.get('Codigo', pd.Series(dtype='str')).astype(str).unique().tolist(),
            key="buscar_codigo"
        )
    with col_search2:
        buscar_nombre = st.selectbox(
            "Buscar por Nombre",
            options=[''] + st.session_state.df_productos['Nombre'].fillna('').unique().tolist(),
            key="buscar_nombre"
        )

    producto_seleccionado = None
    if buscar_codigo:
        try:
            producto_seleccionado = st.session_state.df_productos[st.session_state.df_productos.get('Codigo', pd.Series(dtype='str')).astype(str) == buscar_codigo].iloc[0]
            st.session_state.buscar_nombre = producto_seleccionado['Nombre']
        except Exception as e:
            st.error(f"❌ Error al seleccionar el producto por Código: {e}")
    elif buscar_nombre:
        try:
            producto_seleccionado = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == buscar_nombre].iloc[0]
            st.session_state.buscar_codigo = producto_seleccionado['Codigo']
        except Exception as e:
            st.error(f"❌ Error al seleccionar el producto por Nombre: {e}")

    if producto_seleccionado is not None:
        st.write(f"**Producto Seleccionado: {producto_seleccionado['Nombre']}**")
else:
    st.info("ℹ️ No hay productos disponibles. Por favor, carga un archivo de productos.")

st.subheader("➕ Agregar/Editar Producto")
with st.form(key='agregar_producto_unique'):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        nuevo_codigo = st.text_input(
            "Código",
            value=str(producto_seleccionado['Codigo']) if (producto_seleccionado is not None and 'Codigo' in producto_seleccionado) else "",
            key="nuevo_codigo"
        )
    with col2:
        nuevo_codigo_barras = st.text_input(
            "Código de Barras",
            value=producto_seleccionado['Codigo de Barras'] if (producto_seleccionado is not None and 'Codigo de Barras' in producto_seleccionado) else "",
            key="nuevo_codigo_barras"
        )
    with col3:
        activo = st.checkbox(
            "Activo",
            value=(producto_seleccionado['Activo'] == 'Sí') if (producto_seleccionado is not None and 'Activo' in producto_seleccionado) else False,
            key="activo"
        )

    nuevo_nombre = st.text_input(
        "Nombre",
        value=producto_seleccionado['Nombre'] if (producto_seleccionado is not None and 'Nombre' in producto_seleccionado) else "",
        key="nuevo_nombre"
    )

    nuevo_descripcion = st.text_area(
        "Descripción",
        value=producto_seleccionado['Descripcion'] if (producto_seleccionado is not None and 'Descripcion' in producto_seleccionado) else "",
        height=100,
        key="nuevo_descripcion"
    )

    col4, col5 = st.columns([1, 1])
    with col4:
        alto_valor = 0
        if (producto_seleccionado is not None and
            'Alto' in producto_seleccionado and
            pd.notna(producto_seleccionado['Alto']) and
            str(producto_seleccionado['Alto']).strip().isdigit()):
            alto_valor = int(producto_seleccionado['Alto'])
        nuevo_alto = st.number_input(
            "Alto (cm)",
            min_value=0,
            step=1,
            value=alto_valor,
            key="nuevo_alto"
        )
    with col5:
        ancho_valor = 0
        if (producto_seleccionado is not None and
            'Ancho' in producto_seleccionado and
            pd.notna(producto_seleccionado['Ancho']) and
            str(producto_seleccionado['Ancho']).strip().isdigit()):
            ancho_valor = int(producto_seleccionado['Ancho'])
        nuevo_ancho = st.number_input(
            "Ancho (cm)",
            min_value=0,
            step=1,
            value=ancho_valor,
            key="nuevo_ancho"
        )

    categorias = st.session_state.df_productos['Categorias'].dropna().unique().tolist()
    if producto_seleccionado is not None and 'Categorias' in producto_seleccionado and pd.notna(producto_seleccionado['Categorias']):
        default_categorias = [cat.strip() for cat in producto_seleccionado['Categorias'].split(',')]
    else:
        default_categorias = []
    nueva_categoria = st.multiselect(
        "Categorías",
        options=categorias,
        default=default_categorias,
        key="nueva_categoria"
    )

    st.write("### Proveedor")
    proveedores = st.session_state.df_productos['Proveedor'].dropna().unique().tolist()
    proveedor_seleccionado = st.selectbox(
        "Selecciona un proveedor",
        options=proveedores,
        index=proveedores.index(producto_seleccionado['Proveedor']) if producto_seleccionado is not None and producto_seleccionado['Proveedor'] in proveedores else 0,
        key="proveedor"
    )

    col6,
