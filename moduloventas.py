import streamlit as st
import pandas as pd
from io import BytesIO

# Cargar los datos de clientes y productos desde los archivos correspondientes
file_path_clientes = 'archivo_modificado_clientes_20240928_200050.xlsx'  # Archivo de clientes
file_path_productos = 'archivo_modificado_productos_20240928_201237.xlsx'  # Archivo de productos

df_clientes = pd.read_excel(file_path_clientes)
df_productos = pd.read_excel(file_path_productos)

# Configuración de la página
st.set_page_config(page_title="📁 Módulo de Ventas", layout="wide")

# Título de la aplicación
st.title("📁 Módulo de Ventas")

# Sección de cliente
st.header("🧑‍💼 Datos del Cliente")

# Colocamos el buscador de cliente y el vendedor asignado uno al lado del otro
col1, col2 = st.columns([2, 1])

with col1:
    cliente_seleccionado = st.selectbox(
        "Buscar cliente",[""] + df_clientes['Nombre'].unique(), 
        help="Escribí el nombre del cliente o seleccioná uno de la lista."
    )

    # Solo mostramos los datos del cliente si se ha seleccionado uno
    if cliente_seleccionado:
        cliente_data = df_clientes[df_clientes['Nombre'] == cliente_seleccionado].iloc[0]

        # Colocar debajo de cliente "Descuento" y "Última compra"
        st.write(f"**Descuento:** {cliente_data['Descuento']}%")
        st.write(f"**Última compra:** {cliente_data['Fecha Modificado']}")

with col2:
    # Solo mostramos el vendedor si se ha seleccionado un cliente
    if cliente_seleccionado:
        # Vendedor asignado por defecto es el primero en la lista
        vendedores = cliente_data['Vendedores'].split(',') if pd.notna(cliente_data['Vendedores']) else ['No asignado']
        vendedor_default = vendedores[0]
        vendedor_seleccionado = st.selectbox("Vendedor asignado", vendedores, index=0)

        # Colocar debajo la aclaración "Vendedor asignado" en la segunda columna
        st.write(f"**Vendedor asignado:** {vendedor_seleccionado}")

# Sección de productos
st.header("🛒 Buscador de Productos")

# Tres columnas: Buscador, precio, y stock con colores
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # Buscador de productos con espacio vacío al inicio
    producto_buscado = st.selectbox("Buscar producto", [""] + df_productos['Nombre'].unique().tolist(), 
                                    help="Escribí el nombre del producto o seleccioná uno de la lista.")
    
if producto_buscado:
    producto_data = df_productos[df_productos['Nombre'] == producto_buscado].iloc[0]
    
    with col2:
        # Mostrar precio
        st.write(f"**Precio:** ${producto_data['Precio']}")
    
    with col3:
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
        
        # Campo para seleccionar cantidad si no está forzada la venta por múltiplos
        if stock > 0:
            cantidad = st.number_input("Cantidad", min_value=1, max_value=stock, step=1)
        else:
            cantidad = 0
            st.error("No hay stock disponible para este producto.")
        
        # Botón para agregar el producto al pedido
        if st.button("Agregar producto"):
            # Añadir producto al pedido con la cantidad seleccionada
            if 'pedido' not in st.session_state:
                st.session_state.pedido = []
            
            # Agregar el producto con los detalles
            producto_agregado = {
                'Codigo': producto_data['Codigo'],
                'Nombre': producto_data['Nombre'],
                'Cantidad': cantidad,
                'Precio': producto_data['Precio'],
                'Importe': cantidad * producto_data['Precio']
            }
            st.session_state.pedido.append(producto_agregado)
            st.success(f"Se agregó {cantidad} unidad(es) de {producto_data['Nombre']} al pedido.")
    
    with col_der:
        # Mostrar imagen del producto en la columna aparte
        if pd.notna(producto_data['imagen']) and producto_data['imagen'] != '':
            st.image(producto_data['imagen'], width=200, caption="Imagen del producto")
        else:
            st.write("No hay imagen disponible.")

# Mostrar el pedido actual
if 'pedido' in st.session_state and st.session_state.pedido:
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
        
        # Botón para eliminar producto con tamaño más pequeño y alineado mejor
        eliminar = col6.button('🗑️', key=f"eliminar_{index}")
        if eliminar:
            # Eliminar el producto seleccionado del pedido sin recargar la página
            st.session_state.pedido.pop(index)
            # Reescribir el pedido actual después de eliminar un elemento
            pedido_df = pd.DataFrame(st.session_state.pedido)
    
    # Total de ítems y total del pedido
    total_items = pedido_df['Cantidad'].sum() if not pedido_df.empty else 0
    total_monto = pedido_df['Importe'].sum() if not pedido_df.empty else 0.0

    # Mostrar total de ítems y total del pedido en una sola fila
    col_items, col_total = st.columns([1, 1])
    
    with col_items:
        st.write(f"**Total de items:** {total_items}")
    
    with col_total:
        # Mostrar total del pedido al lado de total de ítems
        st.write(f"<h4 style='text-align:right;'>Total del pedido: ${total_monto:,.2f}</h4>", unsafe_allow_html=True)
    
    # Centrar el botón de guardar pedido
    col_guardar, _ = st.columns([2, 3])
    with col_guardar:
        if st.button("Guardar Pedido"):
            st.success("Pedido guardado exitosamente.", icon="✅")
            
            # Generar un archivo de texto en vez de PDF
            pedido_txt = BytesIO()
            pedido_txt.write(f"Detalles del Pedido\n".encode('utf-8'))
            for index, row in pedido_df.iterrows():
                pedido_txt.write(f"{row['Cantidad']}x {row['Nombre']} - ${row['Importe']:.2f}\n".encode('utf-8'))
            pedido_txt.write(f"\nTotal del pedido: ${total_monto:.2f}".encode('utf-8'))
            pedido_txt.seek(0)
            
            # Proporcionar opción para descargar el archivo de texto
            col_guardar_download = st.columns([2, 1])
            with col_guardar_download[1]:
                st.download_button(label="Descargar Pedido en TXT", data=pedido_txt, file_name="pedido.txt", mime="text/plain")

