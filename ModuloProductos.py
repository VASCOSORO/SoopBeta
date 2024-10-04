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
    nuevo_codigo_barras = st.text_input("Código de Barras", value=producto_seleccionado['Código de Barras'] if producto_seleccionado is not None else "")
    nuevo_nombre = st.text_input("Nombre", value=producto_seleccionado['Nombre'] if producto_seleccionado is not None else "")
    nuevo_descripcion = st.text_area("Descripción", value=producto_seleccionado['Descripción'] if producto_seleccionado is not None else "", height=100)

    # Tamaño (Alto y Ancho)
    col1, col2 = st.columns(2)
    with col1:
        nuevo_alto = st.number_input("Alto (cm)", min_value=0, step=1, value=int(producto_seleccionado['Alto']) if producto_seleccionado is not None and pd.notna(producto_seleccionado['Alto']) and str(producto_seleccionado['Alto']).strip().isdigit() else 0)
    with col2:
        nuevo_ancho = st.number_input("Ancho (cm)", min_value=0, step=1, value=int(producto_seleccionado['Ancho']) if producto_seleccionado is not None and pd.notna(producto_seleccionado['Ancho']) and str(producto_seleccionado['Ancho']).strip().isdigit() else 0)

    # Categorías desplegable
    categorias = st.session_state.df_productos['Categorias'].dropna().unique().tolist()
    if producto_seleccionado is not None and 'Categorias' in producto_seleccionado and pd.notna(producto_seleccionado['Categorias']):
        default_categorias = [cat.strip() for cat in producto_seleccionado['Categorias'].split(',')]
    else:
        default_categorias = []
    nueva_categoria = st.multiselect("Categorías", options=categorias, default=default_categorias)

    # Proveedor desplegable
    proveedores = st.session_state.df_productos['Proveedor'].dropna().unique().tolist()
    proveedor_seleccionado = st.selectbox("Proveedor", options=proveedores, index=proveedores.index(producto_seleccionado['Proveedor']) if producto_seleccionado is not None and producto_seleccionado['Proveedor'] in proveedores else 0)

    # Fila de costos y precios
    st.markdown("---")
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        nuevo_costo_pesos = st.number_input("Costo (Pesos)", min_value=0.0, step=0.01, value=float(producto_seleccionado['Costo (Pesos)']) if producto_seleccionado is not None and pd.notna(producto_seleccionado['Costo (Pesos)']) else 0.0)
    with col4:
        nuevo_costo_usd = st.number_input("Costo (USD)", min_value=0.0, step=0.01, value=float(producto_seleccionado['Costo (USD)']) if producto_seleccionado is not None and pd.notna(producto_seleccionado['Costo (USD)']) else 0.0)
    with col5:
        ultimo_precio_pesos = st.number_input("Último Precio (Pesos)", value=float(producto_seleccionado['Último Precio (Pesos)']) if producto_seleccionado is not None and pd.notna(producto_seleccionado['Último Precio (Pesos)']) else 0.0, disabled=True)
    with col6:
        ultimo_precio_usd = st.number_input("Último Precio (USD)", value=float(producto_seleccionado['Último Precio (USD)']) if producto_seleccionado is not None and pd.notna(producto_seleccionado['Último Precio (USD)']) else 0.0, disabled=True)

    # Marcar último precio en rojo si es menor que el nuevo costo
    if (nuevo_costo_pesos > ultimo_precio_pesos):
        col5.markdown("<p style='color:red;'>Último Precio Menor al Costo</p>", unsafe_allow_html=True)
    if (nuevo_costo_usd > ultimo_precio_usd):
        col6.markdown("<p style='color:red;'>Último Precio Menor al Costo</p>", unsafe_allow_html=True)

    # Fila para Precio y Precio x Mayor con cálculos automáticos
    st.markdown("---")
    col7, col8, col9 = st.columns(3)
    with col7:
        precio_x_mayor = st.number_input("Precio x Mayor", min_value=0.0, step=0.01, value=round(nuevo_costo_pesos * 1.44, 2) if nuevo_costo_pesos else 0.0)
    with col8:
        precio_venta = st.number_input("Precio", min_value=0.0, step=0.01, value=round(precio_x_mayor * 1.13, 2) if precio_x_mayor else 0.0)
    with col9:
        precio_x_menor = st.number_input("Precio x Menor", min_value=0.0, step=0.01, value=round(precio_x_mayor * 1.90, 2) if precio_x_mayor else 0.0)

    # Checkboxes para mostrar precios promocionales
    st.markdown("---")
    st.write("### Precios Promocionales")
    col10, col11, col12 = st.columns(3)
    with col10:
        promo_mayor = st.checkbox("Agregar Precio Promocional x Mayor")
        if promo_mayor:
            precio_promocional_mayor = st.number_input("Precio Promocional x Mayor", min_value=0.0, step=0.01)
        else:
            precio_promocional_mayor = 0.0
    with col11:
        promo_venta = st.checkbox("Agregar Precio Promocional")
        if promo_venta:
            precio_promocional = st.number_input("Precio Promocional", min_value=0.0, step=0.01)
        else:
            precio_promocional = 0.0
    with col12:
        promo_menor = st.checkbox("Agregar Precio Promocional x Menor")
        if promo_menor:
            precio_promocional_menor = st.number_input("Precio Promocional x Menor", min_value=0.0, step=0.01)
        else:
            precio_promocional_menor = 0.0

    # Campos adicionales: Ubicación y Nota
    st.subheader("📍 Campos Adicionales")
    col13, col14, col15 = st.columns(3)
    with col13:
        pasillo = st.text_input("Pasillo", value=producto_seleccionado['Pasillo'] if producto_seleccionado is not None else "")
    with col14:
        estante = st.text_input("Estante", value=producto_seleccionado['Estante'] if producto_seleccionado is not None else "")
    with col15:
        columna = st.text_input("Columna", value=producto_seleccionado['Columna'] if producto_seleccionado is not None else "")

    fecha_vencimiento = st.date_input("📅 Fecha de Vencimiento", value=datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')))
    nota_1 = st.text_area("📝 Nota 1", value=producto_seleccionado['Nota 1'] if producto_seleccionado is not None else "")

    # Botones para guardar o cancelar
    st.markdown("---")
    col16, col17 = st.columns(2)
    with col16:
        guardar = st.form_submit_button(label='Guardar Producto')
    with col17:
        cancelar = st.form_submit_button(label='Cancelar')

    if guardar:
        if not nuevo_codigo or not nuevo_nombre:
            st.error("❌ Por favor, completa los campos obligatorios (Código y Nombre).")
        else:
            # Actualizar o agregar el producto en el DataFrame
            if producto_seleccionado is not None:
                idx = st.session_state.df_productos.index[st.session_state.df_productos['Código'] == producto_seleccionado['Código']].tolist()[0]
                st.session_state.df_productos.loc[idx, 'Código'] = nuevo_codigo
                st.session_state.df_productos.loc[idx, 'Código de Barras'] = nuevo_codigo_barras
                st.session_state.df_productos.loc[idx, 'Nombre'] = nuevo_nombre
                st.session_state.df_productos.loc[idx, 'Descripción'] = nuevo_descripcion
                st.session_state.df_productos.loc[idx, 'Alto'] = nuevo_alto
                st.session_state.df_productos.loc[idx, 'Ancho'] = nuevo_ancho
                st.session_state.df_productos.loc[idx, 'Categorias'] = ','.join(nueva_categoria)
                st.session_state.df_productos.loc[idx, 'Proveedor'] = proveedor_seleccionado
                st.session_state.df_productos.loc[idx, 'Costo (Pesos)'] = nuevo_costo_pesos
                st.session_state.df_productos.loc[idx, 'Costo (USD)'] = nuevo_costo_usd
                st.session_state.df_productos.loc[idx, 'Precio x Mayor'] = precio_x_mayor
                st.session_state.df_productos.loc[idx, 'Precio'] = precio_venta
                st.session_state.df_productos.loc[idx, 'Precio x Menor'] = precio_x_menor
                st.session_state.df_productos.loc[idx, 'Precio Promocional x Mayor'] = precio_promocional_mayor
                st.session_state.df_productos.loc[idx, 'Precio Promocional'] = precio_promocional
                st.session_state.df_productos.loc[idx, 'Precio Promocional x Menor'] = precio_promocional_menor
                st.session_state.df_productos.loc[idx, 'Pasillo'] = pasillo
                st.session_state.df_productos.loc[idx, 'Estante'] = estante
                st.session_state.df_productos.loc[idx, 'Columna'] = columna
                st.session_state.df_productos.loc[idx, 'Fecha de Vencimiento'] = fecha_vencimiento
                st.session_state.df_productos.loc[idx, 'Nota 1'] = nota_1
                st.success("✅ Producto actualizado correctamente.")
            else:
                nuevo_producto = {
                    'Código': nuevo_codigo,
                    'Código de Barras': nuevo_codigo_barras,
                    'Nombre': nuevo_nombre,
                    'Descripción': nuevo_descripcion,
                    'Alto': nuevo_alto,
                    'Ancho': nuevo_ancho,
                    'Categorias': ','.join(nueva_categoria),
                    'Proveedor': proveedor_seleccionado,
                    'Costo (Pesos)': nuevo_costo_pesos,
                    'Costo (USD)': nuevo_costo_usd,
                    'Último Precio (Pesos)': ultimo_precio_pesos,
                    'Último Precio (USD)': ultimo_precio_usd,
                    'Precio x Mayor': precio_x_mayor,
                    'Precio': precio_venta,
                    'Precio x Menor': precio_x_menor,
                    'Precio Promocional x Mayor': precio_promocional_mayor,
                    'Precio Promocional': precio_promocional,
                    'Precio Promocional x Menor': precio_promocional_menor,
                    'Pasillo': pasillo,
                    'Estante': estante,
                    'Columna': columna,
                    'Fecha de Vencimiento': fecha_vencimiento,
                    'Nota 1': nota_1,
                    'Activo': 'Sí'
                }
                st.session_state.df_productos = pd.concat([st.session_state.df_productos, pd.DataFrame([nuevo_producto])], ignore_index=True)
                st.success("✅ Producto agregado correctamente.")

            # Guardar los cambios en el archivo Excel
            try:
                st.session_state.df_productos.to_excel('Produt2.xlsx', index=False, engine='openpyxl')
                st.success("✅ Cambios guardados en 'Produt2.xlsx'.")
            except Exception as e:
                st.error(f"❌ Error al guardar los cambios en 'Produt2.xlsx': {e}")

    if cancelar:
        st.success("✅ Operación cancelada y formulario reseteado.")

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
