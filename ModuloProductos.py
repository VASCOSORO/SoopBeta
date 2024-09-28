import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytz
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import requests
from PIL import Image

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

# Función para asegurar que el valor es al menos el mínimo permitido
def safe_value(value, min_value=0.0):
    return max(value, min_value)

# Lista de categorías válidas (ajustar según tus categorías)
categorias_validas = [
    "Completo Online",
    "Libros y Revistas",
    "Menu Infantil",
    "Ofertas/Saldos",
    "PROM COD 3",
    "Tickets",
    # Agrega más categorías según sea necesario
]

# Sidebar para cargar el archivo Excel
st.sidebar.header("Cargar Archivo Excel de Productos")
uploaded_file = st.sidebar.file_uploader("📤 Subir archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        df = pd.read_excel(uploaded_file, engine='openpyxl')

        # Verificar y agregar columnas para valores anteriores si no existen
        columnas_necesarias = [
            'Stock Anterior', 'Fecha Stock Anterior',
            'Costo Anterior', 'Fecha Costo Anterior',
            'Costo USD Anterior', 'Fecha Costo USD Anterior'
        ]
        for col in columnas_necesarias:
            if col not in df.columns:
                df[col] = None

        # Mostrar los nombres de las columnas para depuración
        st.sidebar.write("🔍 **Columnas en el archivo:**")
        st.sidebar.write(df.columns.tolist())

        # Opciones de filtrado y búsqueda
        st.sidebar.header("Filtrar Productos")
        search_term = st.sidebar.text_input("Buscar por Nombre o Código")

        if search_term:
            df = df[df['Nombre'].str.contains(search_term, case=False, na=False) |
                    df['Codigo'].str.contains(search_term, case=False, na=False)]

        # Filtrado avanzado
        filtro_categoria = st.sidebar.multiselect("Selecciona Categorías", options=categorias_validas)
        filtro_activo = st.sidebar.selectbox("Estado Activo", options=['Todos', 0, 1])

        if filtro_categoria:
            df = df[df['Categorias'].str.contains('|'.join(filtro_categoria), case=False, na=False)]

        if filtro_activo != 'Todos':
            df = df[df['Activo'] == filtro_activo]

        # Configuración de la tabla AgGrid
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(editable=False, groupable=True, resizable=True, sortable=True)
        # Especificar las columnas que se pueden editar (inicialmente no editable)
        columnas_editables = ['Codigo', 'Nombre', 'Precio', 'Precio x Mayor', 'Stock', 'Costo', 'Costo USD', 'Categorias']

        for col in columnas_editables:
            gb.configure_column(col, editable=False)

        # Configuración de formato condicional para Stock Actual
        gb.configure_column("Stock", cellStyle=lambda params: {
            'color': 'red' if params.value < 0 else ('orange' if 1 <= params.value <= 4 else 'green') if params.value > 0 else 'black'
        })

        gridOptions = gb.build()

        # Mostrar la tabla editable con un tema válido y mejor tamaño de columnas
        st.header("📊 Tabla de Productos:")
        grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True,
            theme='streamlit',  # Tema válido
            enable_enterprise_modules=False,
            height=600,
            reload_data=False
        )

        # Obtener el DataFrame modificado
        df_modificado = grid_response['data']

        # Seleccionar un producto con opción inicial vacía
        st.header("🔍 Seleccionar Producto:")
        productos_lista = ["-- Selecciona un producto --"] + df_modificado['Nombre'].tolist()
        selected_product = st.selectbox("Selecciona un Producto", productos_lista)

        if selected_product != "-- Selecciona un producto --":
            producto = df_modificado[df_modificado['Nombre'] == selected_product].iloc[0]

            # Mostrar los detalles del producto
            st.subheader(f"Detalles de: {selected_product}")

            # Organizar los detalles en columnas
            col1, col2 = st.columns([3, 1])

            with col1:
                # Mostrar detalles de forma no editable
                st.markdown(f"**ID:** {producto['Id']}")
                st.markdown(f"**Código:** {producto['Codigo']}")
                st.markdown(f"**Nombre:** {producto['Nombre']}")
                st.markdown(f"**Precio:** ${producto['Precio']:.2f}")
                st.markdown(f"**Precio x Mayor:** ${producto['Precio x Mayor']:.2f}")
                st.markdown(f"**Costo:** ${producto['Costo']:.2f}")
                st.markdown(f"**Costo USD:** ${producto['Costo USD']:.2f}")
                st.markdown(f"**Stock Actual:** {producto['Stock']}")
                st.markdown(f"**Stock Anterior:** {producto['Stock Anterior']} (Última actualización: {producto['Fecha Stock Anterior']})")
                st.markdown(f"**Costo Anterior:** ${producto['Costo Anterior']:.2f} (Última actualización: {producto['Fecha Costo Anterior']})")
                st.markdown(f"**Costo USD Anterior:** ${producto['Costo USD Anterior']:.2f} (Última actualización: {producto['Fecha Costo USD Anterior']})")
                st.markdown(f"**Descripción:** {producto['Descripcion']}")
                st.markdown(f"**Categorías:** {producto['Categorias']}")
                st.markdown(f"**Activo:** {'Sí' if producto['Activo'] == 1 else 'No'}")
                st.markdown(f"**Fecha Creado:** {producto['Fecha Creado']}")
                st.markdown(f"**Fecha Modificado:** {producto['Fecha Modificado']}")

            with col2:
                # Mostrar la imagen del producto
                if pd.notnull(producto['imagen']) and producto['imagen'] != '':
                    try:
                        response = requests.get(producto['imagen'], timeout=5)
                        response.raise_for_status()
                        image = Image.open(BytesIO(response.content))
                        st.image(image, width=150)
                    except Exception as e:
                        st.write("🔗 **Imagen no disponible o URL inválida.**")
                else:
                    st.write("🔗 **No hay imagen disponible.**")

            # Opción para modificar el producto
            modificar = st.checkbox("🔄 Modificar Producto")

            if modificar:
                st.markdown("---")
                st.subheader(f"📝 Editar Detalles de: {selected_product}")

                # Mostrar un formulario con los detalles del producto para editar
                with st.form(key='editar_producto_unique'):
                    # Organizar los campos en columnas para una mejor estética
                    editar_col1, editar_col2 = st.columns([3, 1])

                    with editar_col1:
                        nuevo_codigo = st.text_input("Código", value=producto['Codigo'])
                        nuevo_nombre = st.text_input("Nombre", value=producto['Nombre'])
                        nuevo_precio = st.number_input(
                            "Precio",
                            min_value=0.0,
                            step=0.01,
                            value=float(producto['Precio'])
                        )
                        nuevo_precio_x_mayor = st.number_input(
                            "Precio x Mayor",
                            min_value=0.0,
                            step=0.01,
                            value=safe_value(float(producto['Precio x Mayor']), 0.0)
                        )
                        nuevo_costo = st.number_input(
                            "Costo",
                            min_value=0.0,
                            step=0.01,
                            value=safe_value(float(producto['Costo']), 0.0)
                        )
                        nuevo_costo_usd = st.number_input(
                            "Costo USD",
                            min_value=0.0,
                            step=0.01,
                            value=safe_value(float(producto['Costo USD']), 0.0)
                        )
                        nuevo_stock = st.number_input(
                            "Stock Actual",
                            min_value=-1000,  # Ajustar según necesidades
                            step=1,
                            value=int(producto['Stock'])
                        )
                        # Indicador de color para Stock Actual
                        if nuevo_stock < 0:
                            st.markdown("<span style='color:red;'>📉 Stock Negativo</span>", unsafe_allow_html=True)
                        elif 1 <= nuevo_stock <= 4:
                            st.markdown("<span style='color:orange;'>⚠️ Stock Bajo</span>", unsafe_allow_html=True)
                        elif nuevo_stock > 5:
                            st.markdown("<span style='color:green;'>✅ Stock Suficiente</span>", unsafe_allow_html=True)

                        nuevo_descripcion = st.text_area("Descripción", value=producto['Descripcion'])
                        
                        # Gestión avanzada de categorías
                        st.markdown("**Categorías:**")
                        categorias_seleccionadas = st.multiselect(
                            "Selecciona Categorías",
                            options=categorias_validas,
                            default=producto['Categorias'].split(',') if isinstance(producto['Categorias'], str) else []
                        )
                        categorias_str = ','.join(categorias_seleccionadas)

                    with editar_col2:
                        # Mostrar la imagen del producto
                        if pd.notnull(producto['imagen']) and producto['imagen'] != '':
                            try:
                                response = requests.get(producto['imagen'], timeout=5)
                                response.raise_for_status()
                                image = Image.open(BytesIO(response.content))
                                st.image(image, width=150)
                            except:
                                st.write("🔗 **Imagen no disponible o URL inválida.**")
                        else:
                            st.write("🔗 **No hay imagen disponible.**")

                    submit_edit = st.form_submit_button(label='Guardar Cambios')

                    if submit_edit:
                        # Validaciones
                        if not nuevo_codigo or not nuevo_nombre:
                            st.error("❌ Por favor, completa los campos obligatorios (Código y Nombre).")
                        elif df_modificado['Id'].astype(str).str.contains(str(producto['Id'])).any() and (nuevo_codigo != producto['Codigo']):
                            st.error("❌ El Código ya existe. Por favor, utiliza un Código único.")
                        else:
                            # Guardar valores anteriores
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Stock Anterior'] = producto['Stock']
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Fecha Stock Anterior'] = producto['Fecha Modificado']
                            
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Costo Anterior'] = producto['Costo']
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Fecha Costo Anterior'] = producto['Fecha Modificado']
                            
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Costo USD Anterior'] = producto['Costo USD']
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Fecha Costo USD Anterior'] = producto['Fecha Modificado']
                            
                            # Actualizar los campos modificados
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Codigo'] = nuevo_codigo
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Nombre'] = nuevo_nombre
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Precio'] = nuevo_precio
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Precio x Mayor'] = nuevo_precio_x_mayor
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Costo'] = nuevo_costo
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Costo USD'] = nuevo_costo_usd
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Stock'] = nuevo_stock
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Descripcion'] = nuevo_descripcion
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Categorias'] = categorias_str
                            
                            # Actualizar fecha de modificación
                            argentina = pytz.timezone('America/Argentina/Buenos_Aires')
                            df_modificado.loc[df_modificado['Nombre'] == selected_product, 'Fecha Modificado'] = datetime.now(argentina).strftime("%Y-%m-%d %H:%M:%S")
                            
                            st.success("✅ Producto modificado exitosamente.")

        except Exception as e:
            st.error(f"❌ Ocurrió un error al procesar el archivo: {e}")
    else:
        st.info("📂 Por favor, sube un archivo Excel para comenzar.")

    # Botón para descargar el archivo Excel modificado
    if uploaded_file is not None and 'df_modificado' in locals():
        st.header("💾 Descargar Archivo Modificado:")
        excel = convertir_a_excel(df_modificado)

        # Obtener la fecha y hora actual en horario de Argentina
        argentina = pytz.timezone('America/Argentina/Buenos_Aires')
        timestamp = datetime.now(argentina).strftime("%Y%m%d_%H%M%S")

        # Crear el nombre del archivo con el timestamp
        file_name = f"productos_modificados_{timestamp}.xlsx"

        st.download_button(
            label="📥 Descargar Excel Modificado",
            data=excel,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Funcionalidad para agregar un nuevo producto
        st.header("➕ Agregar Nuevo Producto:")
        with st.form(key='agregar_producto_unique'):
            nuevo_id = st.text_input("Id")
            nuevo_id_externo = st.text_input("Id Externo")
            nuevo_codigo = st.text_input("Código")
            nuevo_nombre = st.text_input("Nombre")
            nuevo_precio_x_mayor = st.number_input("Precio x Mayor", min_value=0.0, step=0.01)
            nuevo_activo = st.selectbox("Activo", options=[0, 1])
            nuevo_fecha_creado = st.date_input("Fecha Creado", value=datetime.now(argentina))
            nuevo_fecha_modificado = st.date_input("Fecha Modificado", value=datetime.now(argentina))
            nuevo_descripcion = st.text_area("Descripción")
            nuevo_orden = st.number_input("Orden", min_value=0, step=1)
            nuevo_codigo_barras = st.text_input("Código de Barras")
            nuevo_unidad_bulto = st.number_input("Unidad por Bulto", min_value=0, step=1)
            nuevo_inner = st.text_input("Inner")
            nuevo_forzar_multiplos = st.text_input("Forzar Multiplos")
            nuevo_costo_usd = st.number_input("Costo USD", min_value=0.0, step=0.01)
            nuevo_costo = st.number_input("Costo", min_value=0.0, step=0.01)
            nuevo_etiquetas = st.text_input("Etiquetas")
            nuevo_stock = st.number_input("Stock", min_value=0, step=1)
            nuevo_precio_mayorista = st.number_input("Precio Mayorista", min_value=0.0, step=0.01)
            nuevo_precio_online = st.number_input("Precio Online", min_value=0.0, step=0.01)
            nuevo_precio = st.number_input("Precio", min_value=0.0, step=0.01)
            nuevo_precio_face_dolar = st.number_input("Precio face Dolar", min_value=0.0, step=0.01)
            nuevo_precio_mayorista_usd = st.number_input("Precio Mayorista USD", min_value=0.0, step=0.01)
            nuevo_marca = st.text_input("Marca")
            # Gestión avanzada de categorías
            st.markdown("**Categorías:**")
            categorias_seleccionadas_agregar = st.multiselect(
                "Selecciona Categorías",
                options=categorias_validas
            )
            categorias_str_agregar = ','.join(categorias_seleccionadas_agregar)
            nuevo_imagen = st.text_input("Imagen URL")
            nuevo_proveedor = st.text_input("Proveedor")
            nuevo_pasillo = st.text_input("Pasillo")
            nuevo_estante = st.text_input("Estante")
            nuevo_fecha_vencimiento = st.date_input("Fecha de Vencimiento", value=datetime.now(argentina))

            submit_nuevo = st.form_submit_button(label='Agregar Producto')

            if submit_nuevo:
                # Validaciones
                if not nuevo_id or not nuevo_nombre or not nuevo_codigo:
                    st.error("❌ Por favor, completa los campos obligatorios (Id, Código y Nombre).")
                elif df_modificado['Id'].astype(str).str.contains(str(nuevo_id)).any():
                    st.error("❌ El Id ya existe. Por favor, utiliza un Id único.")
                elif df_modificado['Codigo'].astype(str).str.contains(nuevo_codigo).any():
                    st.error("❌ El Código ya existe. Por favor, utiliza un Código único.")
                else:
                    # Agregar el nuevo producto al DataFrame
                    nuevo_producto = {
                        'Id': nuevo_id,
                        'Id Externo': nuevo_id_externo,
                        'Codigo': nuevo_codigo,
                        'Nombre': nuevo_nombre,
                        'Precio x Mayor': nuevo_precio_x_mayor,
                        'Activo': nuevo_activo,
                        'Fecha Creado': nuevo_fecha_creado.strftime("%Y-%m-%d"),
                        'Fecha Modificado': datetime.now(argentina).strftime("%Y-%m-%d %H:%M:%S"),
                        'Descripcion': nuevo_descripcion,
                        'Orden': nuevo_orden,
                        'Codigo de Barras': nuevo_codigo_barras,
                        'unidad por bulto': nuevo_unidad_bulto,
                        'inner': nuevo_inner,
                        'forzar multiplos': nuevo_forzar_multiplos,
                        'Costo usd': nuevo_costo_usd,
                        'Costo': nuevo_costo,
                        'Etiquetas': nuevo_etiquetas,
                        'Stock': nuevo_stock,
                        'Precio Mayorista': nuevo_precio_mayorista,
                        'Precio Online': nuevo_precio_online,
                        'Precio': nuevo_precio,
                        'Precio face Dolar': nuevo_precio_face_dolar,
                        'Precio Mayorista USD': nuevo_precio_mayorista_usd,
                        'Marca': nuevo_marca,
                        'Categorias': categorias_str_agregar,
                        'imagen': nuevo_imagen,
                        'Proveedor': nuevo_proveedor,
                        'Pasillo': nuevo_pasillo,
                        'Estante': nuevo_estante,
                        'Fecha de Vencimiento': nuevo_fecha_vencimiento.strftime("%Y-%m-%d"),
                        # Inicializar valores anteriores
                        'Stock Anterior': None,
                        'Fecha Stock Anterior': None,
                        'Costo Anterior': None,
                        'Fecha Costo Anterior': None,
                        'Costo USD Anterior': None,
                        'Fecha Costo USD Anterior': None
                    }
                    df_modificado = df_modificado.append(nuevo_producto, ignore_index=True)
                    st.success("✅ Producto agregado exitosamente.")

else:
    st.info("📂 Por favor, sube un archivo Excel para comenzar.")

# Agregar el footer
agregar_footer()
