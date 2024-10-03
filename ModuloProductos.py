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

# Función para convertir DataFrame a CSV en memoria
def convertir_a_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Función para convertir DataFrame a Excel en memoria usando openpyxl
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Productos')
    return buffer.getvalue()

# Función para agregar el footer
def agregar_footer():
    footer = """
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
    """
    st.markdown(footer, unsafe_allow_html=True)

# Cargar Proveedores desde ProveedoresSoop.xlsx
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
st.sidebar.header("Cargar Archivo CSV o Excel de Productos")
uploaded_file = st.sidebar.file_uploader("📤 Subir archivo CSV o Excel", type=["csv", "xlsx"])

# Cargar proveedores
proveedores = cargar_proveedores()

# Inicializar el DataFrame en session_state para mantener los cambios
if 'df_productos' not in st.session_state:
    st.session_state.df_productos = pd.DataFrame()

if uploaded_file is not None:
    try:
        st.write("📂 **Leyendo archivo...**")
        # Detectar el tipo de archivo subido y leerlo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', sep=None, engine='python', on_bad_lines='skip')
            st.success("✅ **Archivo CSV leído correctamente.**")
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            st.success("✅ **Archivo Excel leído correctamente.**")

        st.write("🔍 **Identificando columnas...**")
        st.write(f"📋 **Columnas identificadas:** {df.columns.tolist()}")

        # Si la columna 'Categorias' no existe, crearla vacía
        if 'Categorias' not in df.columns:
            df['Categorias'] = ''

        # Asignar al session_state
        st.session_state.df_productos = df

    except Exception as e:
        st.error(f"❌ Ocurrió un error al leer el archivo: {e}")
else:
    if 'df_productos' not in st.session_state or st.session_state.df_productos.empty:
        st.info("📂 Por favor, sube un archivo CSV o Excel para comenzar.")

# Mostrar el buscador para buscar un producto para editar
if not st.session_state.df_productos.empty:
    st.subheader("🔍 Buscar Producto para Editar")
    buscar_producto = st.selectbox("Buscar Producto", options=[''] + st.session_state.df_productos['Nombre'].tolist())
else:
    buscar_producto = ''

# Variable para almacenar si se seleccionó un producto
producto_seleccionado = None
if buscar_producto:
    try:
        producto_seleccionado = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == buscar_producto].iloc[0]
        st.write(f"**Producto Seleccionado: {producto_seleccionado['Nombre']}**")
    except Exception as e:
        st.error(f"❌ Error al seleccionar el producto: {e}")

# Función para resetear el formulario
def reset_form():
    for key in ['nuevo_codigo', 'nuevo_codigo_barras', 'activo', 'nuevo_nombre', 'nuevo_descripcion',
                'nuevo_alto', 'nuevo_ancho', 'nueva_categoria', 'nuevo_costo_pesos',
                'nuevo_costo_usd', 'precio_x_mayor', 'precio_venta', 'precio_x_menor',
                'precio_promocional_mayor', 'precio_promocional', 'precio_promocional_menor',
                'pasillo', 'estante', 'columna', 'fecha_vencimiento', 'nota_1', 'proveedor']:
        if key in st.session_state:
            del st.session_state[key]

# Formulario para agregar o editar productos
st.subheader("➕ Agregar/Editar Producto")
with st.form(key='agregar_producto_unique'):
    # Primera fila: Código, Código de Barras, Activo
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        nuevo_codigo = st.text_input("Código", value=str(producto_seleccionado['Código']) if producto_seleccionado is not None else "", key="nuevo_codigo")
    with col2:
        nuevo_codigo_barras = st.text_input("Código de Barras", value=producto_seleccionado['Código de Barras'] if producto_seleccionado is not None else "", key="nuevo_codigo_barras")
    with col3:
        activo = st.checkbox("Activo", value=(producto_seleccionado['Activo'] == 'Sí') if producto_seleccionado is not None else False, key="activo")

    # Segunda fila: Nombre
    nuevo_nombre = st.text_input("Nombre", value=producto_seleccionado['Nombre'] if producto_seleccionado is not None else "", key="nuevo_nombre")

    # Tercera fila: Descripción
    nuevo_descripcion = st.text_area("Descripción", value=producto_seleccionado['Descripción'] if producto_seleccionado is not None else "", height=100, key="nuevo_descripcion")

    # Cuarta fila: Tamaño (Alto y Ancho)
    col4, col5 = st.columns([1, 1])
    with col4:
        nuevo_alto = st.number_input("Alto (cm)", min_value=0, step=1, value=int(producto_seleccionado['Alto']) if (producto_seleccionado is not None and pd.notna(producto_seleccionado['Alto'])) else 0, key="nuevo_alto")
    with col5:
        nuevo_ancho = st.number_input("Ancho (cm)", min_value=0, step=1, value=int(producto_seleccionado['Ancho']) if (producto_seleccionado is not None and pd.notna(producto_seleccionado['Ancho'])) else 0, key="nuevo_ancho")

    # Categorías desplegable
    categorias = st.session_state.df_productos['Categorias'].dropna().unique().tolist()
    nueva_categoria = st.multiselect("Categorías", options=categorias, default=producto_seleccionado['Categorias'].split(',') if (producto_seleccionado is not None and pd.notna(producto_seleccionado['Categorias'])) else [], key="nueva_categoria")

    # Proveedor desplegable
    st.write("### Proveedor")
    if proveedores:
        proveedor_seleccionado = st.selectbox("Selecciona un proveedor", options=proveedores, index=0, key="proveedor")
    else:
        st.warning("⚠️ No hay proveedores disponibles. Por favor, agrégalo desde el módulo correspondiente.")
        proveedor_seleccionado = ""

    # Fila de costos y precios
    st.markdown("---")
    col6, col7, col8, col9 = st.columns([1, 1, 1, 1])
    with col6:
        nuevo_costo_pesos = st.number_input("Costo (Pesos)", min_value=0.0, step=0.01, value=producto_seleccionado['Costo (Pesos)'] if (producto_seleccionado is not None and pd.notna(producto_seleccionado['Costo (Pesos)'])) else 0.0, key="nuevo_costo_pesos")
    with col7:
        nuevo_costo_usd = st.number_input("Costo (USD)", min_value=0.0, step=0.01, value=producto_seleccionado['Costo (USD)'] if (producto_seleccionado is not None and pd.notna(producto_seleccionado['Costo (USD)'])) else 0.0, key="nuevo_costo_usd")
    with col8:
        ultimo_precio_pesos = st.number_input("Último Precio (Pesos)", value=float(producto_seleccionado['Último Precio (Pesos)']) if (producto_seleccionado is not None and pd.notna(producto_seleccionado['Último Precio (Pesos)'])) else 0.0, disabled=True, key="ultimo_precio_pesos")
    with col9:
        ultimo_precio_usd = st.number_input("Último Precio (USD)", value=float(producto_seleccionado['Último Precio (USD)']) if (producto_seleccionado is not None and pd.notna(producto_seleccionado['Último Precio (USD)'])) else 0.0, disabled=True, key="ultimo_precio_usd")

    # Marcar último precio en rojo si es menor que el nuevo costo
    if (nuevo_costo_pesos > ultimo_precio_pesos):
        col8.markdown("<p style='color:red;'>Último Precio Menor al Costo</p>", unsafe_allow_html=True)
    if (nuevo_costo_usd > ultimo_precio_usd):
        col9.markdown("<p style='color:red;'>Último Precio Menor al Costo</p>", unsafe_allow_html=True)

    # Fila para Precio y Precio x Mayor con cálculos automáticos
    st.markdown("---")
    col10, col11, col12 = st.columns([1, 1, 1])
    with col10:
        precio_x_mayor = st.number_input("Precio x Mayor", min_value=0.0, step=0.01, value=round(nuevo_costo_pesos * 1.44, 2) if nuevo_costo_pesos else 0.0, key="precio_x_mayor")
    with col11:
        precio_venta = st.number_input("Precio", min_value=0.0, step=0.01, value=round(precio_x_mayor * 1.13, 2) if precio_x_mayor else 0.0, key="precio_venta")
    with col12:
        precio_x_menor = st.number_input("Precio x Menor", min_value=0.0, step=0.01, value=round(precio_x_mayor * 1.90, 2) if precio_x_mayor else 0.0, key="precio_x_menor")

    # Checkboxes para mostrar precios promocionales
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

    # Campos adicionales: Ubicación y Nota
    st.subheader("📍 Campos Adicionales")
    col16, col17, col18 = st.columns([1, 1, 1])
    with col16:
        pasillo = st.text_input("Pasillo", value=producto_seleccionado['Pasillo'] if (producto_seleccionado is not None and 'Pasillo' in st.session_state.df_productos.columns) else "", key="pasillo")
    with col17:
        estante = st.text_input("Estante", value=producto_seleccionado['Estante'] if (producto_seleccionado is not None and 'Estante' in st.session_state.df_productos.columns) else "", key="estante")
    with col18:
        columna = st.text_input("Columna", value=producto_seleccionado['Columna'] if (producto_seleccionado is not None and 'Columna' in st.session_state.df_productos.columns) else "", key="columna")

    # Fecha de vencimiento y Nota 1
    fecha_vencimiento = st.date_input("📅 Fecha de Vencimiento", value=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')), key="fecha_vencimiento")
    nota_1 = st.text_area("📝 Nota 1", value=producto_seleccionado['Nota 1'] if (producto_seleccionado is not None and 'Nota 1' in st.session_state.df_productos.columns) else "", key="nota_1")

    # Botones para guardar o cancelar
    st.markdown("---")
    col20, col21 = st.columns([1, 1])
    with col20:
        guardar = st.form_submit_button(label='Guardar Producto')
    with col21:
        cancelar = st.form_submit_button(label='Cancelar')

    if guardar:
        try:
            # Generar nuevo ID correlativo
            if 'Código' in st.session_state.df_productos.columns and not st.session_state.df_productos['Código'].empty:
                try:
                    ultimo_id = st.session_state.df_productos['Código'].astype(int).max()
                    nuevo_id = ultimo_id + 1000
                except:
                    nuevo_id = 1000
            else:
                nuevo_id = 1000

            # Crear nuevo producto
            nuevo_producto = pd.DataFrame({
                'Código': [nuevo_id],
                'Código de Barras': [nuevo_codigo_barras],
                'Nombre': [nuevo_nombre],
                'Descripción': [nuevo_descripcion],
                'Alto': [nuevo_alto],
                'Ancho': [nuevo_ancho],
                'Categorias': [','.join(nueva_categoria)],
                'Proveedor': [proveedor_seleccionado],
                'Costo (Pesos)': [nuevo_costo_pesos],
                'Costo (USD)': [nuevo_costo_usd],
                'Último Precio (Pesos)': [0.0],
                'Último Precio (USD)': [0.0],
                'Precio x Mayor': [precio_x_mayor],
                'Precio': [precio_venta],
                'Precio x Menor': [precio_x_menor],
                'Precio Promocional x Mayor': [precio_promocional_mayor],
                'Precio Promocional': [precio_promocional],
                'Precio Promocional x Menor': [precio_promocional_menor],
                'Pasillo': [pasillo],
                'Estante': [estante],
                'Columna': [columna],
                'Fecha de Vencimiento': [fecha_vencimiento],
                'Nota 1': [nota_1],
                'Activo': ['Sí' if activo else 'No']
            })

            # Concatenar el nuevo producto al DataFrame existente
            st.session_state.df_productos = pd.concat([st.session_state.df_productos, nuevo_producto], ignore_index=True)

            st.success("✅ Producto guardado exitosamente.")

            # Resetear el formulario
            reset_form()

        except Exception as e:
            st.error(f"❌ Ocurrió un error al guardar el producto: {e}")

    if cancelar:
        # Resetear el formulario sin guardar
        reset_form()
        st.experimental_rerun()

# Descargar archivo modificado
if not st.session_state.df_productos.empty:
    st.header("💾 Descargar Archivo Modificado:")
    csv = convertir_a_csv(st.session_state.df_productos)
    excel = convertir_a_excel(st.session_state.df_productos)

    argentina = pytz.timezone('America/Argentina/Buenos_Aires')
    timestamp = datetime.now(argentina).strftime("%Y%m%d_%H%M%S")

    # Opción para descargar como CSV
    st.download_button(
        label="📥 Descargar CSV Modificado",
        data=csv,
        file_name=f"productos_modificados_{timestamp}.csv",
        mime="text/csv"
    )

    # Opción para descargar como XLSX
    st.download_button(
        label="📥 Descargar Excel Modificado",
        data=excel,
        file_name=f"productos_modificados_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Agregar el footer
agregar_footer()
