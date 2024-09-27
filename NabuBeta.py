import streamlit as st
import pandas as pd
from datetime import datetime

# Cargar los datos de productos (la tabla que usaste anteriormente)
df_productos = pd.read_excel("archivo_modificado_corregido.xlsx")  # Asegurate de tener tu archivo cargado

# Inicializar variables para la venta
vendedores = ['Emily', 'Joni', 'Johan', 'Valen', 'Marian', 'Sofi', 'Aniel', 'Mostrador']
venta = []

# Título de la aplicación
st.title("Sistema de Gestión de Ventas")

# Seleccionar vendedor
vendedor = st.selectbox("Seleccioná el vendedor", vendedores)

# Ingresar datos del cliente
cliente = st.text_input("Nombre del Cliente", "")

# Tabla para almacenar la venta
st.write("Artículos agregados:")

# Campos para seleccionar productos
producto_seleccionado = st.selectbox("Seleccioná un artículo", df_productos["Nombre"].values)
cantidad = st.number_input("Cantidad", min_value=1, value=1)
precio_unitario = df_productos[df_productos["Nombre"] == producto_seleccionado]["Precio"].values[0]
subtotal = cantidad * precio_unitario

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
    if cliente and vendedor and venta:
        # Guardar los datos de la venta en un archivo CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df_venta["Vendedor"] = vendedor
        df_venta["Cliente"] = cliente
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
