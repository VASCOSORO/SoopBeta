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
    'Codigo', 'Codigo de Barras', 'Nombre', 'Descripcion',
    'Alto', 'Ancho', 'Categorias', 'Proveedor',
    'Costo (Pesos)', 'Costo (USD)', 'Ultimo Precio (Pesos)',
    'Ultimo Precio (USD)', 'Precio x Mayor', 'Precio',
    'Precio x Menor', 'Precio Promocional x Mayor',
    'Precio Promocional', 'Precio Promocional x Menor',
    'Pasillo', 'Estante', 'Columna', 'Fecha de Vencimiento',
    'Nota 1', 'Activo'
]

def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Productos')
    return buffer.getvalue()

def cargar_y_convertir_csv():
    csv_path = 'Produt2.csv'
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, encoding='ISO-8859-1', sep=None, engine='python', on_bad_lines='skip')
            st.success("✅ **Archivo CSV leído correctamente.**")

            st.write("🔍 **Identificando columnas...**")
            st.write(f"📋 **Columnas identificadas:** {df.columns.tolist()}")

            df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

            if 'precio jugueterias face' in df.columns:
                df.rename(columns={'precio jugueterias face': 'Precio', 'precio': 'Precio x Mayor'}, inplace=True)
            if 'precio' in df.columns:
                df.rename(columns={'precio jugueterias face': 'Precio', 'precio': 'Precio x Mayor'}, inplace=True)

            if 'Categorias' not in df.columns:
                df['Categorias'] = ''

            for col in columnas_esperadas:
                if col not in df.columns:
                    df[col] = ''

            df = df[columnas_esperadas]

            df['Ultima Actualizacion'] = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%Y-%m-%d %H:%M:%S")

            df.to_excel('Produt2.xlsx', index=False, engine='openpyxl')
            st.success("✅ Archivo 'Produt2.csv' convertido y guardado como 'Produt2.xlsx'.")

            st.write("### Vista Previa de los Datos Convertidos:")
            st.dataframe(df.head(10))

            return df
        except Exception as e:
            st.error(f"❌ Error al convertir 'Produt2.csv': {e}")
    else:
        st.warning("⚠️ El archivo 'Produt2.csv' no se encontró en la carpeta raíz.")
    return None

st.sidebar.header("📥 Cargar y Convertir Archivo de Productos")
if st.sidebar.button("Cargar 'Produt2.csv' y Convertir a Excel"):
    df_convertido = cargar_y_convertir_csv()
    if df_convertido is not None:
        if st.button("Confirmar Conversión y Usar Archivo 'Produt2.xlsx'"):
            st.session_state.df_productos = df_convertido
            st.success("✅ Confirmación recibida. Ahora se utilizará 'Produt2.xlsx' para las modificaciones.")

if 'df_productos' not in st.session_state:
    if os.path.exists('Produt2.xlsx'):
        try:
            st.session_state.df_productos = pd.read_excel('Produt2.xlsx', engine='openpyxl')
        except Exception as e:
            st.session_state.df_productos = pd.DataFrame(columns=columnas_esperadas)
            st.error(f"❌ Error al leer 'Produt2.xlsx': {e}")
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
            options=[''] + st.session_state.df_productos['Nombre'].unique().tolist(),
            key="buscar_nombre"
        )

    producto_seleccionado = None
    if buscar_codigo:
        try:
            producto_seleccionado = st.session_state.df_productos[st.session_state.df_productos.get('Codigo', pd.Series(dtype='str')).astype(str) == buscar_codigo].iloc[0]
            st.write(f"**Producto Seleccionado por Código: {producto_seleccionado['Nombre']}**")
        except Exception as e:
            st.error(f"❌ Error al seleccionar el producto por Código: {e}")
    elif buscar_nombre:
        try:
            producto_seleccionado = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == buscar_nombre].iloc[0]
            st.write(f"**Producto Seleccionado por Nombre: {producto_seleccionado['Nombre']}**")
        except Exception as e:
            st.error(f"❌ Error al seleccionar el producto por Nombre: {e}")
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
        index=0,
        key="proveedor"
    )

    st.markdown("---")
    col6, col7, col8, col9 = st.columns([1, 1, 1, 1])
    with col6:
        nuevo_costo_pesos = 0.0
        if producto_seleccionado is not None and 'Costo (Pesos)' in producto_seleccionado and pd.notna(producto_seleccionado['Costo (Pesos)']):
            try:
                nuevo_costo_pesos = float(producto_seleccionado['Costo (Pesos)'])
            except (ValueError, TypeError):
                nuevo_costo_pesos = 0.0
        nuevo_costo_pesos = st.number_input(
            "Costo (Pesos)",
            min_value=0.0,
            step=0.01,
            value=nuevo_costo_pesos,
            key="nuevo_costo_pesos"
        )
    with col7:
        nuevo_costo_usd = 0.0
        if producto_seleccionado is not None and 'Costo (USD)' in producto_seleccionado and pd.notna(producto_seleccionado['Costo (USD)']):
            try:
                nuevo_costo_usd = float(producto_seleccionado['Costo (USD)'])
            except (ValueError, TypeError):
                nuevo_costo_usd = 0.0
        nuevo_costo_usd = st.number_input(
            "Costo (USD)",
            min_value=0.0,
            step=0.01,
            value=nuevo_costo_usd,
            key="nuevo_costo_usd"
        )
    with col8:
        ultimo_precio_pesos = 0.0
        if producto_seleccionado is not None and 'Ultimo Precio (Pesos)' in producto_seleccionado and pd.notna(producto_seleccionado['Ultimo Precio (Pesos)']):
            try:
                ultimo_precio_pesos = float(producto_seleccionado['Ultimo Precio (Pesos)'])
            except (ValueError, TypeError):
                ultimo_precio_pesos = 0.0
        ultimo_precio_pesos = st.number_input(
            "Último Precio (Pesos)",
            value=ultimo_precio_pesos,
            disabled=True,
            key="ultimo_precio_pesos"
        )
    with col9:
        ultimo_precio_usd = 0.0
        if producto_seleccionado is not None and 'Ultimo Precio (USD)' in producto_seleccionado and pd.notna(producto_seleccionado['Ultimo Precio (USD)']):
            try:
                ultimo_precio_usd = float(producto_seleccionado['Ultimo Precio (USD)'])
            except (ValueError, TypeError):
                ultimo_precio_usd = 0.0
        ultimo_precio_usd = st.number_input(
            "Último Precio (USD)",
            value=ultimo_precio_usd,
            disabled=True,
            key="ultimo_precio_usd"
        )

    if nuevo_costo_pesos > ultimo_precio_pesos:
        col8.markdown("<p style='color:red;'>Último Precio Menor al Costo</p>", unsafe_allow_html=True)
    if nuevo_costo_usd > ultimo_precio_usd:
        col9.markdown("<p style='color:red;'>Último Precio Menor al Costo</p>", unsafe_allow_html=True)

    st.markdown("---")
    col10, col11, col12 = st.columns([1, 1, 1])
    with col10:
        precio_x_mayor = st.number_input(
            "Precio x Mayor",
            min_value=0.0,
            step=0.01,
            value=round(nuevo_costo_pesos * 1.44, 2) if nuevo_costo_pesos else 0.0,
            key="precio_x_mayor"
        )
    with col11:
        precio_venta = st.number_input(
            "Precio",
            min_value=0.0,
            step=0.01,
            value=round(precio_x_mayor * 1.13, 2) if precio_x_mayor else 0.0,
            key="precio_venta"
        )
    with col12:
        precio_x_menor = st.number_input(
            "Precio x Menor",
            min_value=0.0,
            step=0.01,
            value=round(precio_x_mayor * 1.90, 2) if precio_x_mayor else 0.0,
            key="precio_x_menor"
        )

    st.markdown("---")
    st.write("### Precios Promocionales")
    col13, col14, col15 = st.columns([1, 1, 1])
    with col13:
        promo_mayor = st.checkbox("Agregar Precio Promocional x Mayor", key="promo_mayor")
        if promo_mayor:
            precio_promocional_mayor = st.number_input("Precio Promocional x Mayor", min_value=0.0, step=0.01, key="precio_promocional_mayor")
        else:
            precio_promocional_mayor = 0.0
    with col14:
        promo_venta = st.checkbox("Agregar Precio Promocional", key="promo_venta")
        if promo_venta:
            precio_promocional = st.number_input("Precio Promocional", min_value=0.0, step=0.01, key="precio_promocional")
        else:
            precio_promocional = 0.0
    with col15:
        promo_menor = st.checkbox("Agregar Precio Promocional x Menor", key="promo_menor")
        if promo_menor:
            precio_promocional_menor = st.number_input("Precio Promocional x Menor", min_value=0.0, step=0.01, key="precio_promocional_menor")
        else:
            precio_promocional_menor = 0.0

    st.subheader("📍 Campos Adicionales")
    col16, col17, col18 = st.columns([1, 1, 1])
    with col16:
        pasillo = st.text_input(
            "Pasillo",
            value=producto_seleccionado['Pasillo'] if (producto_seleccionado is not None and 'Pasillo' in producto_seleccionado and pd.notna(producto_seleccionado['Pasillo'])) else "",
            key="pasillo"
        )
    with col17:
        estante = st.text_input(
            "Estante",
            value=producto_seleccionado['Estante'] if (producto_seleccionado is not None and 'Estante' in producto_seleccionado and pd.notna(producto_seleccionado['Estante'])) else "",
            key="estante"
        )
    with col18:
        columna = st.text_input(
            "Columna",
            value=producto_seleccionado['Columna'] if (producto_seleccionado is not None and 'Columna' in producto_seleccionado and pd.notna(producto_seleccionado['Columna'])) else "",
            key="columna"
        )

    fecha_vencimiento = st.date_input(
        "📅 Fecha de Vencimiento",
        value=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')),
        key="fecha_vencimiento"
    )
    nota_1 = st.text_area(
        "📝 Nota 1",
        value=producto_seleccionado['Nota 1'] if (producto_seleccionado is not None and 'Nota 1' in producto_seleccionado and pd.notna(producto_seleccionado['Nota 1'])) else "",
        key="nota_1"
    )

    st.markdown("---")
    col20, col21 = st.columns([1, 1])
    with col20:
        guardar = st.form_submit_button(label='Guardar Producto')
    with col21:
        cancelar = st.form_submit_button(label='Cancelar')

    if guardar:
        try:
            if not nuevo_codigo or not nuevo_nombre:
                st.error("❌ Por favor, completa los campos obligatorios (Código y Nombre).")
            elif nuevo_codigo in st.session_state.df_productos.get('Codigo', pd.Series(dtype='str')).astype(str).tolist() and (producto_seleccionado is None or str(producto_seleccionado['Codigo']) != nuevo_codigo):
                st.error("❌ El Código ya existe. Por favor, utiliza un Código único.")
            else:
                es_nuevo = producto_seleccionado is None

                if es_nuevo:
                    try:
                        df_numerico = st.session_state.df_productos.get('Codigo', pd.Series(dtype='str')).astype(str).str.extract('(\d+)').drop
