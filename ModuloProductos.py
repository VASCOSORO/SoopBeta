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
            value=nuevo_costo_pesos,
            key="nuevo_costo_pesos"
        )
    with col7:
        try:
            nuevo_costo_usd = float(producto_seleccionado['Costo (USD)']) if (
                producto_seleccionado is not None and
                'Costo (USD)' in producto_seleccionado and
                pd.notna(producto_seleccionado['Costo (USD)'])
            ) else 0.0
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
        try:
            ultimo_precio_pesos = float(producto_seleccionado['Último Precio (Pesos)']) if (
                producto_seleccionado is not None and
                'Último Precio (Pesos)' in producto_seleccionado and
                pd.notna(producto_seleccionado['Último Precio (Pesos)'])
            ) else 0.0
        except (ValueError, TypeError):
            ultimo_precio_pesos = 0.0
        ultimo_precio_pesos = st.number_input(
            "Último Precio (Pesos)",
            value=ultimo_precio_pesos,
            disabled=True,
            key="ultimo_precio_pesos"
        )
    with col9:
        try:
            ultimo_precio_usd = float(producto_seleccionado['Último Precio (USD)']) if (
                producto_seleccionado is not None and
                'Último Precio (USD)' in producto_seleccionado and
                pd.notna(producto_seleccionado['Último Precio (USD)'])
            ) else 0.0
        except (ValueError, TypeError):
            ultimo_precio_usd = 0.0
        ultimo_precio_usd = st.number_input(
            "Último Precio (USD)",
            value=ultimo_precio_usd,
            disabled=True,
            key="ultimo_precio_usd"
        )

    # Marcar último precio en rojo si es menor que el nuevo costo
    if (nuevo_costo_pesos > ultimo_precio_pesos):
        col8.markdown("<p style='color:red;'>Último Precio Menor al Costo</p>", unsafe_allow_html=True)
    if (nuevo_costo_usd > ultimo_precio_usd):
        col9.markdown("<p style='color:red;'>Último Precio Menor al Costo</p>", unsafe_allow_html=True)

    # Fila para Precio y Precio x Mayor con cálculos automáticos
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

    # Fecha de vencimiento y Nota 1
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

    # Botones para guardar o cancelar
    st.markdown("---")
    col20, col21 = st.columns([1, 1])
    with col20:
        guardar = st.form_submit_button(label='Guardar Producto')
    with col21:
        cancelar = st.form_submit_button(label='Cancelar')

    if guardar:
        try:
            # Validaciones básicas
            if not nuevo_codigo or not nuevo_nombre:
                st.error("❌ Por favor, completa los campos obligatorios (Código y Nombre).")
            elif nuevo_codigo in st.session_state.df_productos['Código'].astype(str).tolist() and (producto_seleccionado is None or str(producto_seleccionado['Código']) != nuevo_codigo):
                st.error("❌ El Código ya existe. Por favor, utiliza un Código único.")
            else:
                # Determinar si es un nuevo producto o una actualización
                es_nuevo = producto_seleccionado is None

                # Generar nuevo ID correlativo solo si es un nuevo producto
                if es_nuevo:
                    try:
                        # Intentar extraer números del 'Código' para encontrar el máximo
                        df_numerico = st.session_state.df_productos['Código'].astype(str).str.extract('(\d+)').dropna().astype(int)
                        if not df_numerico.empty:
                            ultimo_id = df_numerico[0].max()
                            nuevo_id = ultimo_id + 1
                        else:
                            nuevo_id = 1000
                    except:
                        nuevo_id = 1000
                else:
                    nuevo_id = producto_seleccionado['Código']

                # Crear nuevo producto o actualizar existente
                nuevo_producto = {
                    'Código': nuevo_id,
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
                    'Activo': 'Sí' if activo else 'No'
                }

                if es_nuevo:
                    # Agregar nuevo producto utilizando pd.concat en lugar de append
                    st.session_state.df_productos = pd.concat([st.session_state.df_productos, pd.DataFrame([nuevo_producto])], ignore_index=True)
                    st.success("✅ Producto agregado exitosamente.")
                else:
                    # Actualizar producto existente
                    idx = st.session_state.df_productos.index[st.session_state.df_productos['Código'] == producto_seleccionado['Código']].tolist()[0]
                    st.session_state.df_productos.loc[idx] = nuevo_producto
                    st.success("✅ Producto actualizado exitosamente.")

                # Resetear el formulario
                reset_form()

        except Exception as e:
            st.error(f"❌ Ocurrió un error al guardar el producto: {e}")

    if cancelar:
        # Resetear el formulario sin guardar
        reset_form()
        st.success("✅ Operación cancelada y formulario reseteado.")
