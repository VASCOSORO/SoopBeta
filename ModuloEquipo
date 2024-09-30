import streamlit as st
import pandas as pd
from openpyxl import load_workbook, Workbook
import json
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(page_title="🛒 Módulo de Ventas", layout="wide")

# Título de la aplicación
st.title("🐻 Módulo de Ventas 🛒")

# Función para listar hojas en un archivo Excel
def listar_hojas_excel(file_path):
    try:
        workbook = load_workbook(filename=file_path, read_only=True)
        return workbook.sheetnames
    except Exception as e:
        st.error(f"Error al abrir el archivo {file_path}: {e}")
        return []

# Inicializar el estado del pedido y el stock si no existen
if 'pedido' not in st.session_state:
    st.session_state.pedido = []

# Definir los nombres de las hojas
nombre_hoja_productos = 'Hoja 1'  # Nombre correcto de la hoja de productos

# Cargar DataFrame de productos
if 'df_productos' not in st.session_state:
    file_path_productos = 'archivo_modificado_productos_20240928_201237.xlsx'  # Archivo de productos
    hojas_productos = listar_hojas_excel(file_path_productos)
    if nombre_hoja_productos in hojas_productos:
        try:
            st.session_state.df_productos = pd.read_excel(file_path_productos, sheet_name=nombre_hoja_productos)
        except Exception as e:
            st.error(f"Error al cargar la hoja '{nombre_hoja_productos}' del archivo de productos: {e}")
            st.stop()
    else:
        st.error(f"La hoja '{nombre_hoja_productos}' no existe en el archivo de productos. Hojas disponibles: {hojas_productos}")
        st.stop()

# Cargar DataFrame de clientes
if 'df_clientes' not in st.session_state:
    file_path_clientes = 'archivo_modificado_clientes_20240928_200050.xlsx'  # Archivo de clientes
    try:
        st.session_state.df_clientes = pd.read_excel(file_path_clientes)
    except Exception as e:
        st.error(f"Error al cargar el archivo de clientes: {e}")
        st.stop()

# Definir el archivo de pedidos
file_path_pedidos = 'PedidosSoop.xlsx'  # Archivo de pedidos

# Función para guardar el pedido en PedidosSoop.xlsx
def guardar_pedido_excel_pedidos(order_data):
    try:
        if not os.path.exists(file_path_pedidos):
            # Crear un nuevo libro y agregar la hoja 'Pedidos' con encabezados
            book = Workbook()
            sheet = book.active
            sheet.title = 'Pedidos'
            sheet.append(['ID Pedido', 'Cliente', 'Vendedor', 'Fecha', 'Hora', 'Items'])
        else:
            book = load_workbook(file_path_pedidos)
            if 'Pedidos' in book.sheetnames:
                sheet = book['Pedidos']
            else:
                sheet = book.create_sheet('Pedidos')
                sheet.append(['ID Pedido', 'Cliente', 'Vendedor', 'Fecha', 'Hora', 'Items'])
        
        # Generar ID de pedido
        if sheet.max_row == 1:
            id_pedido = 1
        else:
            last_id = sheet['A'][sheet.max_row].value
            id_pedido = last_id + 1 if last_id is not None else 1
        
        # Formatear los ítems como JSON
        items_json = json.dumps(order_data['items'], ensure_ascii=False)
        
        # Agregar nueva fila
        sheet.append([
            id_pedido,
            order_data['cliente'],
            order_data['vendedor'],
            order_data['fecha'],
            order_data['hora'],
            items_json
        ])
        
        # Guardar el libro
        book.save(file_path_pedidos)
    except Exception as e:
        st.error(f"Error al guardar el pedido en {file_path_pedidos}: {e}")

# Función para actualizar el stock en el archivo de productos
def actualizar_stock_productos():
    try:
        with pd.ExcelWriter(file_path_productos, engine='openpyxl', mode='w') as writer:
            st.session_state.df_productos.to_excel(writer, sheet_name=nombre_hoja_productos, index=False)
    except Exception as e:
        st.error(f"Error al actualizar el stock en el archivo de productos: {e}")

# Colocamos el buscador de cliente
col1, col2 = st.columns([2, 1])

with col1:
    cliente_seleccionado = st.selectbox(
        "🔮 Buscar cliente", [""] + st.session_state.df_clientes['Nombre'].unique().tolist(),
        help="Escribí el nombre del cliente o seleccioná uno de la lista."
    )

# Solo mostramos los demás campos si se selecciona un cliente distinto al espacio vacío
if cliente_seleccionado != "":
    cliente_data = st.session_state.df_clientes[st.session_state.df_clientes['Nombre'] == cliente_seleccionado].iloc[0]

    # Mostrar descuento y última compra
    with col1:
        st.write(f"**Descuento:** {cliente_data['Descuento']}%")
        st.write(f"**Última compra:** {cliente_data['Fecha Modificado']}")

    # Mostrar vendedor principal
    with col2:
        vendedores = cliente_data['Vendedores'].split(',') if pd.notna(cliente_data['Vendedores']) else ['No asignado']
        vendedor_default = vendedores[0]
        vendedor_seleccionado = st.selectbox("Vendedor", vendedores, index=0)
        st.write(f"**Vendedor Principal:** {vendedor_seleccionado}")

    # Sección de productos solo aparece si hay cliente seleccionado
    st.header("📁 Buscador de Productos 🔍")

    # Tres columnas: Buscador, precio, y stock con colores
    col_prod1, col_prod2, col_prod3 = st.columns([2, 1, 1])

    with col_prod1:
        # Buscador de productos con espacio vacío al inicio
        producto_buscado = st.selectbox(
            "Buscar producto",
            [""] + st.session_state.df_productos['Nombre'].unique().tolist(),
            help="Escribí el nombre del producto o seleccioná uno de la lista."
        )

    if producto_buscado:
        producto_data = st.session_state.df_productos[st.session_state.df_productos['Nombre'] == producto_buscado].iloc[0]

        with col_prod2:
            # Mostrar precio
            st.write(f"**Precio:** ${producto_data['Precio']}")

        with col_prod3:
            # Mostrar stock con colores según la cantidad
            stock = max(0, producto_data['Stock'])  # Nos aseguramos que el stock no sea negativo
            if stock <= 0:
                color = 'red'
            elif stock < 10:
                color = 'orange'
            else:
                color = 'green'

            st.markdown(f"<span style='color:{color}'>**Stock disponible:** {stock}</span>", unsafe_allow_html=True)

        # Dividimos la sección en dos columnas para mostrar el código y la cantidad en la izquierda, y la imagen a la derecha
        col_izq, col_der = st.columns([2, 1])

        with col_izq:
            # Mostrar código del producto
            st.write(f"**Código del producto:** {producto_data['Codigo']}")

            # Verificar si la venta está forzada por múltiplos
            if pd.notna(producto_data['forzar multiplos']) and producto_data['forzar multiplos'] > 0:
                st.warning(f"Este producto tiene venta forzada por {int(producto_data['forzar multiplos'])} unidades.")
                cantidad = st.number_input(
                    "Cantidad",
                    min_value=int(producto_data['forzar multiplos']),
                    step=int(producto_data['forzar multiplos']),
                    key=f"cantidad_{producto_data['Codigo']}"
                )
            else:
                # Campo para seleccionar cantidad si no está forzada la venta por múltiplos
                if stock > 0:
                    cantidad = st.number_input(
                        "Cantidad",
                        min_value=1,
                        max_value=stock,
                        step=1,
                        key=f"cantidad_{producto_data['Codigo']}"
                    )
                else:
                    cantidad = 0
                    st.error("No hay stock disponible para este producto.")

            # Botón para agregar el producto al pedido, deshabilitado si no hay stock
            boton_agregar_desactivado = stock <= 0  # Deshabilitar el botón si no hay stock
            if st.button("Agregar producto", disabled=boton_agregar_desactivado, key=f"agregar_{producto_data['Codigo']}"):
                # Verificar si el producto ya está en el pedido
                existe = any(item['Codigo'] == producto_data['Codigo'] for item in st.session_state.pedido)
                if existe:
                    st.warning("Este producto ya está en el pedido. Por favor, ajusta la cantidad si es necesario.")
                else:
                    # Añadir producto al pedido con la cantidad seleccionada
                    producto_agregado = {
                        'Codigo': producto_data['Codigo'],
                        'Nombre': producto_data['Nombre'],
                        'Cantidad': cantidad,
                        'Precio': producto_data['Precio'],
                        'Importe': cantidad * producto_data['Precio']
                    }
                    st.session_state.pedido.append(producto_agregado)
                    # Descontar del stock en el DataFrame de productos
                    st.session_state.df_productos.loc[
                        st.session_state.df_productos['Codigo'] == producto_data['Codigo'], 'Stock'
                    ] -= cantidad
                    st.success(f"Se agregó {cantidad} unidad(es) de {producto_data['Nombre']} al pedido.")

        with col_der:
            # Mostrar imagen del producto en la columna aparte
            if pd.notna(producto_data['imagen']) and producto_data['imagen'] != '':
                st.image(producto_data['imagen'], width=200, caption="Imagen del producto")
            else:
                st.write("No hay imagen disponible.")

    # Mostrar el pedido actual
    if st.session_state.pedido:
        st.header("📦 Pedido actual")

        # Convertir la lista de productos en un DataFrame
        pedido_df = pd.DataFrame(st.session_state.pedido)

        # Mostrar la tabla del pedido con la opción de eliminar ítems
        for index, row in pedido_df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 1])
            col1.write(row['Codigo'])
            col2.write(row['Nombre'])
            col3.write(row['Cantidad'])
            col4.write(f"${row['Precio']}")
            col5.write(f"${row['Importe']}")

            # Botón para eliminar el ítem
            eliminar_clicked = col6.button('🗑️', key=f"eliminar_{index}")
            if eliminar_clicked:
                # Eliminar el ítem del pedido
                producto = st.session_state.pedido.pop(index)
                # Reponer el stock en el DataFrame de productos
                st.session_state.df_productos.loc[
                    st.session_state.df_productos['Codigo'] == producto['Codigo'], 'Stock'
                ] += producto['Cantidad']
                st.success(f"Se eliminó {producto['Nombre']} del pedido.")

        # Actualizar el DataFrame después de posibles cambios
        if st.session_state.pedido:
            pedido_df = pd.DataFrame(st.session_state.pedido)
        else:
            pedido_df = pd.DataFrame()

        # Total de ítems y total del pedido
        total_items = pedido_df['Cantidad'].sum() if not pedido_df.empty else 0
        total_monto = pedido_df['Importe'].sum() if not pedido_df.empty else 0.0

        # Mostrar total de ítems y total del pedido en una sola fila
        col_items, col_total = st.columns([1, 1])

        with col_items:
            st.write(f"**Total de ítems:** {total_items}")

        with col_total:
            # Mostrar total del pedido al lado de total de ítems
            st.write(f"<h4 style='text-align:right;'>Total del pedido: ${total_monto:,.2f}</h4>", unsafe_allow_html=True)

        # Centrar el botón de guardar pedido
        col_guardar, _ = st.columns([2, 3])
        with col_guardar:
            if st.button("Guardar Pedido"):
                if not st.session_state.pedido:
                    st.warning("No hay ítems en el pedido para guardar.")
                else:
                    # Obtener fecha y hora actuales
                    now = datetime.now()
                    fecha_actual = now.strftime("%Y-%m-%d")
                    hora_actual = now.strftime("%H:%M:%S")

                    # Preparar datos del pedido
                    order_data = {
                        'cliente': cliente_seleccionado,
                        'vendedor': vendedor_seleccionado,
                        'fecha': fecha_actual,
                        'hora': hora_actual,
                        'items': st.session_state.pedido
                    }

                    # Guardar el pedido en PedidosSoop.xlsx
                    guardar_pedido_excel_pedidos(order_data)

                    # Confirmar al usuario
                    st.success("Pedido guardado exitosamente en PedidosSoop.xlsx.", icon="✅")

                    # Limpiar el pedido después de guardarlo
                    st.session_state.pedido = []

                    # Guardar los cambios en el stock de productos
                    actualizar_stock_productos()
