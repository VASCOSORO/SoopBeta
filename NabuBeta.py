import streamlit as st
import pandas as pd
from datetime import datetime

# Cargar los datos de productos y clientes
df_productos = pd.read_excel("archivo_modificado_corregido.xlsx")  # Asegurate de tener el archivo de productos cargado
df_clientes = pd.read_csv("ClientesMundo27sep.csv", encoding='ISO-8859-1', sep=';', on_bad_lines='skip')

# Extraer nombres de clientes y vendedores
clientes = df_clientes["Nombre"].fillna("Cliente desconocido").tolist()

# Inicializar lista de vendedores
vendedores = ['Emily', 'Joni', 'Johan', 'Valen', 'Marian', 'Sofi', 'Aniel', 'Mostrador']

# Título de la aplicación
st.title("Sistema de Gestión de Ventas")

# Crear columnas para el desplegable "+ Datos" y el selector de vendedor
col_datos, col_vendedor = st.columns([2, 2])

# Mostrar el botón "+ Datos" y desplegar información adicional del cliente
with col_datos:
    if st.checkbox("+ Datos"):
        cliente_seleccionado = st.selectbox("Seleccioná el Cliente", clientes)
        cliente_info = df_clientes[df_clientes["Nombre"] == cliente_seleccionado]
        if not cliente_info.empty:
            # Mostrar datos en columnas
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Teléfono**: {cliente_info['Telefono'].values[0]}")
                st.write(f"**CUIT/DNI**: {cliente_info['CUIT'].values[0]}")
            with col_b:
                st.write(f"**Celular**: {cliente_info['Celular'].values[0]}")
                st.write(f"**Dirección**: {cliente_info['Direccion'].values[0]}, {cliente_info['Ciudad'].values[0]}, {cliente_info['Provincia'].values[0]}")

# Vinculación automática del vendedor y advertencia si se cambia
with col_vendedor:
    cliente_seleccionado = st.selectbox("Seleccioná el Cliente", clientes, key="cliente_selector")
    cliente_info = df_clientes[df_clientes["Nombre"] == cliente_seleccionado]
    vendedor_defecto = cliente_info["Vendedores"].values[0] if not cliente_info.empty else "Mostrador"
    vendedor = st.selectbox("Seleccioná el Vendedor", vendedores, index=vendedores.index(vendedor_defecto) if vendedor_defecto in vendedores else 0)

    if vendedor != vendedor_defecto:
        st.success(f"Advertencia: {vendedor} no es el vendedor por defecto de este cliente.")

# Mostrar el descuento del cliente fuera del desplegable
descuento_cliente = cliente_info['Descuento'].values[0] if not cliente_info.empty else 0
st.write(f"**Descuento**: {descuento_cliente}%")

# Mostrar solo el ícono de WhatsApp
celular = cliente_info['Celular'].values[0] if not cliente_info.empty else None
if celular:
    whatsapp_link = f"https://wa.me/{celular}"
    st.markdown(f'<a href="{whatsapp_link}" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="25"/></a>', unsafe_allow_html=True)

# Selector de productos
producto_seleccionado = st.selectbox("Seleccioná un artículo", df_productos["Nombre"].values)

# Mostrar imagen del producto más pequeña al costado
col_prod, col_img = st.columns([2, 1])
with col_prod:
    st.write(f"Producto seleccionado: {producto_seleccionado}")
    precio_unitario = df_productos[df_productos["Nombre"] == producto_seleccionado]["Precio"].values[0]
    st.write(f"Precio unitario: ${precio_unitario}")

with col_img:
    imagen_url = df_productos[df_productos["Nombre"] == producto_seleccionado]["imagen"].values[0]
    if imagen_url:
        st.image(imagen_url, width=100)

# Campo para cantidad
cantidad = st.number_input("Cantidad", min_value=1, value=1)

# Verificar si la venta está forzada
venta_forzada = df_productos[df_productos["Nombre"] == producto_seleccionado]["forzar multiplos"].values[0]
if venta_forzada:
    st.write("Venta forzada: El precio es por unidad y será multiplicado por la cantidad seleccionada.")
subtotal = cantidad * precio_unitario

# Inicializar la lista de ventas
if 'venta' not in st.session_state:
    st.session_state['venta'] = []

# Botón para agregar el ítem a la venta
if st.button("Agregar Ítem"):
    st.session_state['venta'].append({
        "Producto": producto_seleccionado,
        "Cantidad": cantidad,
        "Precio Unitario": precio_unitario,
        "Subtotal": subtotal
    })

# Mostrar la tabla con los productos agregados
if st.session_state['venta']:
    st.subheader("Items en la venta:")
    df_venta = pd.DataFrame(st.session_state['venta'])
    st.table(df_venta)
    total = df_venta["Subtotal"].sum()
    st.write(f"Total: ${total}")

# Botón para guardar la venta
if st.button("Guardar Venta"):
    if cliente_seleccionado and vendedor_defecto and st.session_state['venta']:
        # Guardar los datos de la venta en un archivo CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df_venta["Vendedor"] = vendedor_defecto
        df_venta["Cliente"] = cliente_seleccionado
        df_venta["Fecha"] = timestamp
        df_venta["Total"] = total
        
        # Cargar el archivo de ventas (o crear uno nuevo si no existe)
        try:
            df_historial = pd.read_csv("historial_ventas.csv")
        except FileNotFoundError:
            df_historial = pd.DataFrame()

        # Agregar la nueva venta al historial
        df_historial = pd.concat([df_historial, df_venta], ignore_index=True)

        # Guardar el historial actualizado
        df_historial.to_csv("historial_ventas.csv", index=False)

        st.success("Venta guardada exitosamente")
        st.session_state['venta'] = []  # Limpiar la venta después de guardarla
    else:
        st.error("Debe ingresar el nombre del cliente y seleccionar al menos un artículo")
