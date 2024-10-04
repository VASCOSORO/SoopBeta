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

# Función para convertir DataFrame a Excel en memoria usando openpyxl
def convertir_a_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Productos')
    return buffer.getvalue()

# Función para cargar archivo Produt2.csv y convertir a Produt2.xlsx
def cargar_y_convertir_csv():
    csv_path = 'Produt2.csv'
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, encoding='ISO-8859-1', sep=None, engine='python', on_bad_lines='skip')
            st.success("✅ **Archivo CSV leído correctamente.**")

            st.write("🔍 **Identificando columnas...**")
            st.write(f"📋 **Columnas identificadas:** {df.columns.tolist()}")

            # Si la columna 'Categorias' no existe, crearla vacía
            if 'Categorias' not in df.columns:
                df['Categorias'] = ''

            # Asegurarse de que todas las columnas esperadas existan
            for col in columnas_esperadas:
                if col not in df.columns:
                    df[col] = ''

            # Reordenar las columnas según `columnas_esperadas`
            df = df[columnas_esperadas]

            # Agregar columna de fecha de última actualización
            df['Última Actualización'] = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%Y-%m-%d %H:%M:%S")

            # Guardar como Excel
            df.to_excel('Produt2.xlsx', index=False, engine='openpyxl')
            st.success("✅ Archivo 'Produt2.csv' convertido y guardado como 'Produt2.xlsx'.")

            # Mostrar vista previa
            st.write("### Vista Previa de los Datos Convertidos:")
            st.dataframe(df.head(10))

            return df
        except Exception as e:
            st.error(f"❌ Error al convertir 'Produt2.csv': {e}")
    else:
        st.warning("⚠️ El archivo 'Produt2.csv' no se encontró en la carpeta raíz.")
    return None

# Sidebar para cargar el archivo CSV y convertirlo a Excel
st.sidebar.header("📥 Cargar y Convertir Archivo de Productos")
if st.sidebar.button("Cargar 'Produt2.csv' y Convertir a Excel"):
    df_convertido = cargar_y_convertir_csv()
    if df_convertido is not None:
        if st.button("Confirmar Conversión y Usar Archivo 'Produt2.xlsx'"):
            st.session_state.df_productos = df_convertido
            st.success("✅ Confirmación recibida. Ahora se utilizará 'Produt2.xlsx' para las modificaciones.")

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
    # Crear dos buscadores independientes: uno para Código y otro para Nombre
    col_search1, col_search2 = st.columns(2)
    with col_search1:
        buscar_codigo = st.selectbox(
            "Buscar por Código",
            options=[''] + st.session_state.df_productos['Código'].astype(str).unique().tolist(),
            key="buscar_codigo"
        )
    with col_search2:
        buscar_nombre = st.selectbox(
            "Buscar por Nombre",
            options=[''] + st.session_state.df_productos['Nombre'].unique().tolist(),
            key="buscar_nombre"
        )

    # Variable para almacenar si se seleccionó un producto
    producto_seleccionado = None
    if buscar_codigo:
        try:
            producto_seleccionado = st.session_state.df_productos[st.session_state.df_productos['Código'].astype(str) == buscar_codigo].iloc[0]
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

# Formulario para agregar o editar productos
st.subheader("➕ Agregar/Editar Producto")
with st.form(key='agregar_producto_unique'):
    # Primera fila: Código, Código de Barras, Activo
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        nuevo_codigo = st.text_input(
            "Código",
            value=str(producto_seleccionado['Código']) if (producto_seleccionado is not None and 'Código' in producto_seleccionado) else "",
            key="nuevo_codigo"
        )
    with col2:
        nuevo_codigo_barras = st.text_input(
            "Código de Barras",
            value=producto_seleccionado['Código de Barras'] if (producto_seleccionado is not None and 'Código de Barras' in producto_seleccionado) else "",
            key="nuevo_codigo_barras"
        )
    with col3:
        activo = st.checkbox(
            "Activo",
            value=(producto_seleccionado['Activo'] == 'Sí') if (producto_seleccionado is not None and 'Activo' in producto_seleccionado) else False,
            key="activo"
        )

    # Segunda fila: Nombre
    nuevo_nombre = st.text_input(
        "Nombre",
        value=producto_seleccionado['Nombre'] if (producto_seleccionado is not None and 'Nombre' in producto_seleccionado) else "",
        key="nuevo_nombre"
    )

    # Tercera fila: Descripción
    nuevo_descripcion = st.text_area(
        "Descripción",
        value=producto_seleccionado['Descripción'] if (producto_seleccionado is not None and 'Descripción' in producto_seleccionado) else "",
        height=100,
        key="nuevo_descripcion"
    )

    # Cuarta fila: Tamaño (Alto y Ancho)
    col4, col5 = st.columns([1, 1])
    with col4:
        # Manejo seguro del valor 'Alto'
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
        # Manejo seguro del valor 'Ancho'
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

    # Categorías desplegable
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

    # Proveedor desplegable
    st.write("### Proveedor")
    proveedores = st.session_state.df_productos['Proveedor'].dropna().unique().tolist()
    proveedor_seleccionado = st.selectbox(
        "Selecciona un proveedor",
        options=proveedores,
        index=0,
        key="proveedor"
    )

    # Fila de costos y precios
    st.markdown("---")
    col6, col7, col8, col9 = st.columns([1, 1, 1, 1])
    with col6:
        try:
            nuevo_costo_pesos = float(producto_seleccionado['Costo (Pesos)']) if (
                producto_seleccionado is not None and
                'Costo (Pesos)' in producto_seleccionado and
                pd.notna(producto_seleccionado['Costo (Pesos)'])
            ) else 0.0
        except (ValueError, TypeError):
            nuevo_costo_pesos = 0.0
        nuevo_costo_pesos = st.number_input(
            "Costo (Pesos)",
            min_value=0.0,
            step=0.01,
