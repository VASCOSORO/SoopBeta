import streamlit as st
import pandas as pd
from datetime import datetime

# Cargar los datos de productos y clientes
df_productos = pd.read_excel("archivo_modificado_corregido.xlsx")  # Cargar el archivo de productos
df_clientes = pd.read_csv("ClientesMundo27sep.csv", encoding='ISO-8859-1', sep=';', on_bad_lines='skip')

# Extraer nombres de clientes y vendedores
clientes = df_clientes["Nombre"].fillna("Cliente desconocido").tolist()
vendedores_por_defecto = df_clientes["Vendedores"].fillna("Mostrador").tolist()

# Inicializar lista de vendedores
vendedores = ['Emily', 'Joni', 'Johan', 'Valen', 'Marian', 'Sofi', 'Aniel', 'Mostrador']

# Título de la aplicación
st.title("Sistema de Gestión de Ventas")

# Crear columnas para dividir la interfaz
col1, col2 = st.columns([2, 1])

# Seleccionar cliente
with col1:
    cliente_seleccionado = st.selectbox("Seleccioná el Cliente", clientes)

# Mostrar checkbox para desplegar más datos del cliente
if st.checkbox("+ Datos"):
    cliente_info = df_clientes[df_clientes["Nombre"] == cliente_seleccionado]
    if not cliente_info.empty:
        st.subheader("Datos del Cliente")
        st.write(f"**CUIT/DNI**: {cliente_info['CUIT'].values[0]}")
        st.write(f"**Dirección**: {cliente_info['Direccion'].values[0]}, {cliente_info['Ciudad'].values[0]}, {cliente_info['Provincia'].values[0]}")
        st.write(f"**Teléfono**: {cliente_info['Telefono'].values[0]}")
        st.write(f"**Celular**: {cliente_info['Celular'].values[0]}")
        st.write(f"**Descuento**: {cliente_info['Descuento'].values[0]}%")
        st.write(f"**Notas**: {cliente_info['Notas'].values[0]}")

        # Enlace de WhatsApp
        celular = cliente_info['Celular'].values[0]
        if celular:
            whatsapp_link = f"https://wa.me/{celular}?text=Hola,%20tengo%20una%20consulta."
            st.markdown(f"[Enviar WhatsApp]({whatsapp_link})", unsafe_allow_html=True)

# Encontrar el vendedor por defecto asociado al cliente seleccionado
vendedor_defecto = df_clientes[df_clientes["Nombre"] == cliente_seleccionado]["Vendedores"].values[0]

# Seleccionar vendedor (por defecto, el asociado al cliente)
with col2:
    vendedor = st.selectbox("Seleccioná el Vendedor", vendedores, index=vendedores.index(vendedor_defecto) if vendedor_defecto in vendedores else 0)

# Mostrar artículos agregados
st.write("Artículos agregados:")

# Selector de productos
producto_seleccionado = st.selectbox("Seleccioná un artículo", df_productos["Nombre"].values)

# Mostrar imagen del producto seleccionado
imagen_url = df_productos[df_productos["Nombre"] == producto_seleccionado]["imagen"].values[0]
if imagen_url:
    st.image(imagen_url, caption=producto_seleccionado)

# Campo para cantidad
cantidad = st.number_input("Cantidad", min_value=1, value=1)

# Verificar si la columna "Precio" existe
if "Precio" in df_productos.columns:
    precio_unitario = df_productos[df_productos["Nombre"] == producto_seleccionado]["Precio"].values[0]
else:
    st.error("La columna 'Precio' no existe en el archivo.")

# Mostrar el precio unitario y forzar venta si es necesario
venta_forzada = df_productos[df_productos["Nombre"] == producto_seleccionado]["forzar multiplos"].values[0]
st.write(f"Precio unitario: ${precio_unitario}")
if venta_forzada:
    st.write("Venta forzada: El precio es por unidad y será multiplicado por la cantidad seleccionada.")
subtotal = cantidad * precio_unitario

# Inicializar la lista de ventas
venta = []

# Agregar a la venta
if st.button("Agregar"):
    venta.append({"Producto": producto_seleccionado, "Cantidad": cantidad, "Precio Unitario": precio_unitario, "Subtotal": subtotal})

# Mostrar la venta actual
if venta:
    df_venta = pd.DataFrame(venta)
    st.table(df_venta)
    total = df_venta["Subtotal"].sum()
    st.write(f"Total: ${total}")

# Botón para guardar la venta
if st.button("Guardar Venta"):
    if cliente_seleccionado and vendedor and venta:
        # Guardar los datos de la venta en un archivo CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df_venta["Vendedor"] = vendedor
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
    else:
        st.error("Debe ingresar el nombre del cliente y seleccionar al menos un artículo")
