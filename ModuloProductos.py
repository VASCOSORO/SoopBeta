# ===== Módulo Productos 2.0.2 ANDA BASTATE BIEN DE VISTA POR LO MNEOS ======
# ===========================================

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

# Definición de las columnas esperadas
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

            # Normalizar nombres de columnas
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

            # Añadir columnas faltantes
            for col in columnas_esperadas:
                if col not in df.columns:
                    df[col] = ''

            # Reordenar columnas
            df = df[columnas_esperadas]

            # Añadir o actualizar la columna de última actualización
            df['Ultima Actualizacion'] = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%Y-%m-%d %H:%M:%S")

            # Guardar el DataFrame actualizado
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

# Cargar datos al inicio y mantener en el estado de la sesión
if 'df_productos' not in st.session_state:
    df_convertido = cargar_excel()
    if df_convertido is not None:
        st.session_state.df_productos = df_convertido
    else:
        st.session_state.df_productos = pd.DataFrame(columns=columnas_esperadas)

# Sección de búsqueda de productos
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

# Sección para agregar o editar productos
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
        options=proveedores if proveedores else ["Seleccione..."],
        index=0,
        key="proveedor"
    )

    col6, col7, col8 = st.columns([1, 1, 1])
    with col6:
        unidades_por_bulto = st.number_input(
            "Unidades por Bulto",
            min_value=0,
            step=1,
            value=int(producto_seleccionado['Unidades por Bulto']) if (producto_seleccionado is not None and 'Unidades por Bulto' in producto_seleccionado and pd.notna(producto_seleccionado['Unidades por Bulto'])) else 0,
            key="unidades_por_bulto"
        )
    with col7:
        presentacion = st.text_input(
            "Presentación/Paquete/Bolsa/Display",
            value=producto_seleccionado['Presentacion'] if (producto_seleccionado is not None and 'Presentacion' in producto_seleccionado) else "",
            key="presentacion"
        )
    with col8:
        fecha_vencimiento = st.date_input(
            "Fecha de Vencimiento",
            value=datetime.strptime(producto_seleccionado['Fecha de Vencimiento'], "%Y-%m-%d").date() if (producto_seleccionado is not None and 'Fecha de Vencimiento' in producto_seleccionado and pd.notna(producto_seleccionado['Fecha de Vencimiento'])) else datetime.today(),
            key="fecha_vencimiento"
        )

    # Continuación del formulario con más campos según las columnas esperadas
    st.write("### Precios y Costos")
    col9, col10, col11 = st.columns([1, 1, 1])
    with col9:
        costo_pesos = st.number_input(
            "Costo (Pesos)",
            min_value=0.0,
            step=0.01,
            value=float(producto_seleccionado['Costo (Pesos)']) if (producto_seleccionado is not None and 'Costo (Pesos)' in producto_seleccionado and pd.notna(producto_seleccionado['Costo (Pesos)'])) else 0.0,
            key="costo_pesos"
        )
    with col10:
        costo_usd = st.number_input(
            "Costo (USD)",
            min_value=0.0,
            step=0.01,
            value=float(producto_seleccionado['Costo (USD)']) if (producto_seleccionado is not None and 'Costo (USD)' in producto_seleccionado and pd.notna(producto_seleccionado['Costo (USD)'])) else 0.0,
            key="costo_usd"
        )
    with col11:
        precio_venta = st.number_input(
            "Precio Venta (Pesos)",
            min_value=0.0,
            step=0.01,
            value=float(producto_seleccionado['Precio Venta']) if (producto_seleccionado is not None and 'Precio Venta' in producto_seleccionado and pd.notna(producto_seleccionado['Precio Venta'])) else 0.0,
            key="precio_venta"
        )

    st.write("### Ubicación en Tienda")
    col12, col13, col14 = st.columns([1, 1, 1])
    with col12:
        pasillo = st.text_input(
            "Pasillo",
            value=producto_seleccionado['Pasillo'] if (producto_seleccionado is not None and 'Pasillo' in producto_seleccionado) else "",
            key="pasillo"
        )
    with col13:
        estante = st.text_input(
            "Estante",
            value=producto_seleccionado['Estante'] if (producto_seleccionado is not None and 'Estante' in producto_seleccionado) else "",
            key="estante"
        )
    with col14:
        columna = st.text_input(
            "Columna",
            value=producto_seleccionado['Columna'] if (producto_seleccionado is not None and 'Columna' in producto_seleccionado) else "",
            key="columna"
        )

    # Campo para subir imagen (opcional)
    st.write("### Imagen del Producto")
    imagen = st.file_uploader(
        "Subir imagen",
        type=['png', 'jpg', 'jpeg'],
        key="imagen"
    )
    if imagen:
        # Convertir imagen a bytes y luego a una cadena base64 si se desea almacenar en Excel
        imagen_bytes = imagen.read()
        imagen_nombre = imagen.name
        # Aquí puedes decidir cómo manejar la imagen, por ejemplo, guardarla en una carpeta y almacenar la ruta
        ruta_imagen = os.path.join("imagenes_productos", imagen_nombre)
        os.makedirs("imagenes_productos", exist_ok=True)
        with open(ruta_imagen, "wb") as f:
            f.write(imagen_bytes)
        st.success(f"✅ Imagen '{imagen_nombre}' subida correctamente.")
    else:
        ruta_imagen = producto_seleccionado['Imagen'] if (producto_seleccionado is not None and 'Imagen' in producto_seleccionado) else ""

    # Botón de envío del formulario
    submit_button = st.form_submit_button(label='Guardar Producto')

    if submit_button:
        # Validaciones básicas
        if not nuevo_codigo:
            st.error("❌ El campo 'Código' es obligatorio.")
        elif not nuevo_nombre:
            st.error("❌ El campo 'Nombre' es obligatorio.")
        elif not proveedor_seleccionado or proveedor_seleccionado == "Seleccione...":
            st.error("❌ Debes seleccionar un proveedor.")
        else:
            # Preparar los datos del producto
            nuevo_producto = {
                'id': producto_seleccionado['id'] if (producto_seleccionado is not None and 'id' in producto_seleccionado) else len(st.session_state.df_productos) + 1,
                'id externo': producto_seleccionado['id externo'] if (producto_seleccionado is not None and 'id externo' in producto_seleccionado) else "",
                'Codigo': nuevo_codigo,
                'Codigo de Barras': nuevo_codigo_barras,
                'Nombre': nuevo_nombre,
                'Descripcion': nuevo_descripcion,
                'Alto': nuevo_alto,
                'Ancho': nuevo_ancho,
                'Categorias': ', '.join(nueva_categoria),
                'Proveedor': proveedor_seleccionado,
                'Costo (Pesos)': costo_pesos,
                'Costo (USD)': costo_usd,
                'Ultimo Precio (Pesos)': producto_seleccionado['Ultimo Precio (Pesos)'] if (producto_seleccionado is not None and 'Ultimo Precio (Pesos)' in producto_seleccionado) else 0.0,
                'Ultimo Precio (USD)': producto_seleccionado['Ultimo Precio (USD)'] if (producto_seleccionado is not None and 'Ultimo Precio (USD)' in producto_seleccionado) else 0.0,
                'Precio x Mayor': producto_seleccionado['Precio x Mayor'] if (producto_seleccionado is not None and 'Precio x Mayor' in producto_seleccionado) else 0.0,
                'Precio Venta': precio_venta,
                'Precio x Menor': producto_seleccionado['Precio x Menor'] if (producto_seleccionado is not None and 'Precio x Menor' in producto_seleccionado) else 0.0,
                'Precio Promocional x Mayor': producto_seleccionado['Precio Promocional x Mayor'] if (producto_seleccionado is not None and 'Precio Promocional x Mayor' in producto_seleccionado) else 0.0,
                'Precio Promocional': producto_seleccionado['Precio Promocional'] if (producto_seleccionado is not None and 'Precio Promocional' in producto_seleccionado) else 0.0,
                'Precio Promocional x Menor': producto_seleccionado['Precio Promocional x Menor'] if (producto_seleccionado is not None and 'Precio Promocional x Menor' in producto_seleccionado) else 0.0,
                'Pasillo': pasillo,
                'Estante': estante,
                'Columna': columna,
                'Fecha de Vencimiento': fecha_vencimiento.strftime("%Y-%m-%d"),
                'Nota 1': producto_seleccionado['Nota 1'] if (producto_seleccionado is not None and 'Nota 1' in producto_seleccionado) else "",
                'Activo': 'Sí' if activo else 'No',
                'Imagen': ruta_imagen,
                'Unidades por Bulto': unidades_por_bulto,
                'Venta Forzada': producto_seleccionado['Venta Forzada'] if (producto_seleccionado is not None and 'Venta Forzada' in producto_seleccionado) else "",
                'Presentacion': presentacion,
                'Ultima Actualizacion': datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).strftime("%Y-%m-%d %H:%M:%S")
            }

            # Si se está editando un producto existente
            if producto_seleccionado is not None:
                df_index = st.session_state.df_productos.index[st.session_state.df_productos['id'] == nuevo_producto['id']].tolist()
                if df_index:
                    st.session_state.df_productos.loc[df_index[0]] = nuevo_producto
                    st.success(f"✅ **Producto '{nuevo_nombre}' actualizado exitosamente.**")
            else:
                # Agregar un nuevo producto
                st.session_state.df_productos = st.session_state.df_productos.append(nuevo_producto, ignore_index=True)
                st.success(f"✅ **Producto '{nuevo_nombre}' agregado exitosamente.**")

            # Guardar los cambios en el archivo Excel
            try:
                st.session_state.df_productos.to_excel('Produt2.xlsx', index=False, engine='openpyxl')
                st.success("✅ Los cambios han sido guardados en 'Produt2.xlsx'.")
            except Exception as e:
                st.error(f"❌ Error al guardar los cambios en 'Produt2.xlsx': {e}")

            # Actualizar la vista previa
            st.write("### Vista Previa de los Datos Actualizados:")
            st.dataframe(st.session_state.df_productos.head(10))

            # Resetear los campos del formulario si se desea
            st.session_state.buscar_codigo = ''
            st.session_state.buscar_nombre = ''

# Opcional: Mostrar todos los productos en una tabla
st.subheader("📊 Todos los Productos")
st.dataframe(st.session_state.df_productos)

# Opcional: Descargar la base de datos actualizada
def descargar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

st.download_button(
    label="📥 Descargar Base de Datos Actualizada",
    data=descargar_excel(st.session_state.df_productos),
    file_name='Produt2_actualizado.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)
