import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import json
from datetime import datetime

# Inicializar el estado del pedido y el stock si no existen
if 'pedido' not in st.session_state:
    st.session_state.pedido = []

if 'df_productos' not in st.session_state:
    file_path_productos = 'archivo_modificado_productos_20240928_201237.xlsx'  # Archivo de productos
    try:
        st.session_state.df_productos = pd.read_excel(file_path_productos)
    except Exception as e:
        st.error(f"Error al cargar el archivo de productos: {e}")
        st.stop()

if 'df_clientes' not in st.session_state:
    file_path_clientes = 'archivo_modificado_clientes_20240928_200050.xlsx'  # Archivo de clientes
    try:
        st.session_state.df_clientes = pd.read_excel(file_path_clientes)
    except Exception as e:
        st.error(f"Error al cargar el archivo de clientes: {e}")
        st.stop()

# Inicializar 'pending_deletions' si no existe
if 'pending_deletions' not in st.session_state:
    st.session_state.pending_deletions = set()

# Función para guardar el pedido en la hoja 'Pedidos' del archivo de productos
def guardar_pedido_excel(file_path, order_data):
    try:
        book = load_workbook(file_path)
        if 'Pedidos' in book.sheetnames:
            sheet = book['Pedidos']
        else:
            sheet = book.create_sheet('Pedidos')
            # Escribir encabezados
            sheet.append(['ID Pedido', 'Cliente', 'Vendedor', 'Fecha', 'Hora', 'Items'])
        
        # Generar ID de pedido
        if sheet.max_row == 1:
            id_pedido = 1
        else:
            last_id = sheet['A'][sheet.max_row - 1].value
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
        book.save(file_path)
    except Exception as e:
        st.error(f"Error al guardar el pedido: {e}")

# Funciones para manejar la eliminación de ítems
def confirm_delete(codigo):
    # Encontrar el índice del producto con el Código específico
    index = next((i for i, item in enumerate(st.session_state.pedido) if item['Codigo'] == codigo), None)
    if index is not None:
        producto_eliminado = st.session_state.pedido.pop(index)
        # Reponer el stock
        st.session_state.df_productos.loc[
            st.session_state.df_productos['Codigo'] == producto_eliminado['Codigo'], 'Stock'
        ] += producto_eliminado['Cantidad']
    # Limpiar el indicador de eliminación
    st.session_state.delete_code = None

def cancel_delete(codigo):
    # Remover el código del set de pending_deletions
    st.session_state.pending_deletions.discard(codigo)

# Configuración de la página
st.set_page_config(page_title="🛒 Módulo de Ventas", layout="wide")

# Título de la aplicación
st.title("🐻 Módulo de Ventas 🛒")

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
                    # Descontar del stock
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

        # Mostrar la tabla del pedido con la opción de eliminar ítems
        for producto in st.session_state.pedido.copy():  # Use copy to avoid modification during iteration
            codigo = producto['Codigo']
            nombre = producto['Nombre']
            cantidad = producto['Cantidad']
            precio = producto['Precio']
            importe = producto['Importe']

            # Crear columnas para mostrar el producto y el botón de eliminar
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 1])
            col1.write(codigo)
            col2.write(nombre)
            col3.write(cantidad)
            col4.write(f"${precio}")
            col5.write(f"${importe}")

            # Verificar si este producto está pendiente de eliminación
            if codigo in st.session_state.pending_deletions:
                # Mostrar botón de confirmación en rojo o con un emoji de advertencia
                with col6:
                    st.markdown("<span style='color: red; font-weight: bold;'>⚠️</span>", unsafe_allow_html=True)
                    if st.button("Sí", key=f"confirmar_si_{codigo}"):
                        # Eliminar el ítem del pedido
                        index = next((i for i, item in enumerate(st.session_state.pedido) if item['Codigo'] == codigo), None)
                        if index is not None:
                            producto_eliminado = st.session_state.pedido.pop(index)
                            # Reponer el stock
                            st.session_state.df_productos.loc[
                                st.session_state.df_productos['Codigo'] == producto_eliminado['Codigo'], 'Stock'
                            ] += producto_eliminado['Cantidad']
                        # Remover del set de pending_deletions
                        st.session_state.pending_deletions.remove(codigo)

                    if st.button("No", key=f"confirmar_no_{codigo}"):
                        # Cancelar la eliminación
                        st.session_state.pending_deletions.remove(codigo)
            else:
                # Mostrar el botón de eliminar normal
                with col6:
                    if st.button('🗑️', key=f"eliminar_{codigo}"):
                        # Marcar este ítem para eliminación
                        st.session_state.pending_deletions.add(codigo)

        # Calcular totales
        pedido_df = pd.DataFrame(st.session_state.pedido)
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

                    # Guardar el pedido en la hoja 'Pedidos'
                    guardar_pedido_excel(file_path_productos, order_data)

                    # Confirmar al usuario
                    st.success("Pedido guardado exitosamente.", icon="✅")

                    # Limpiar el pedido después de guardarlo
                    st.session_state.pedido = []

                    # Guardar los cambios en el stock de productos
                    try:
                        with pd.ExcelWriter(file_path_productos, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                            st.session_state.df_productos.to_excel(writer, sheet_name='Hoja1', index=False)
                    except Exception as e:
                        st.error(f"Error al actualizar el stock en el archivo de productos: {e}")
