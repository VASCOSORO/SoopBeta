import streamlit as st
import pandas as pd
from datetime import datetime

# Cargar los datos de productos y clientes
df_productos = pd.read_excel("archivo_modificado_corregido.xlsx")  # Asegurate de tener tu archivo cargado

# Leer el archivo CSV de clientes con el delimitador correcto
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

# Encontrar el vendedor por defecto asociado al cliente seleccionado
vendedor_defecto = df_clientes[df_clientes["Nombre"] == cliente_seleccionado]["Vendedores"].values[0]

# Seleccionar vendedor (por defecto, el asociado al cliente)
with col2:
    vendedor = st.selectbox("Seleccioná el Vendedor", vendedores, index=vendedores.index(vendedor_defecto) if vendedor_defecto in vendedores else 0)

# Mostrar artículos agregados
st.write("Artículos agregados:")

# Selector de productos
producto_seleccionado = st.selectbox("Seleccioná un artículo", df_productos["Nombre"].values)

# Campo para cantidad
cantidad = st.number_input("Cantidad", min_value=1, value=1)

# Verificar si la columna "Precio" existe
if "Precio" in df_productos.columns:
    precio_unitario = df_productos[df_productos["Nombre"] == producto_seleccionado]["Precio"].values[0]
else:
    st.error("La columna 'Precio' no existe en el archivo.")

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
