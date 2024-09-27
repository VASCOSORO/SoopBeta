import pandas as pd
from google.colab import files
import io

# 1. Subir archivo CSV
print("Subí tu archivo CSV")
uploaded = files.upload()

# 2. Leer el archivo CSV subido con el delimitador adecuado
for filename in uploaded.keys():
    # Usamos ';' como delimitador
    df = pd.read_csv(io.BytesIO(uploaded[filename]), encoding='ISO-8859-1', sep=';', on_bad_lines='skip', engine='python')

# 3. Renombrar las columnas que especificaste
df = df.rename(columns={
    'Costo FOB': 'Costo en U$s',  # Cambio de 'Costo FOB' a 'Costo en U$s'
    'Precio jugueteria Face': 'Precio',  # Cambio de 'Precio Jugueteria Face' a 'Precio'
    'Precio': 'Precio x Mayor'  # Cambio de 'Precio' a 'Precio x Mayor'
})

# 4. Eliminar columnas que no sirven
df = df.drop(columns=['Precio Face + 50', 'Precio Bonus'], errors='ignore')

# 5. Agregar nuevas columnas vacías (pueden completarse luego)
df['Proveedor'] = ''
df['Pasillo'] = ''
df['Estante'] = ''
df['Fecha de Vencimiento'] = ''

# 6. Guardar el archivo en formato Excel
df.to_excel('archivo_modificado_corregido.xlsx', index=False)

# 7. Descargar el archivo modificado
print("Tu archivo modificado se está descargando...")
files.download('archivo_modificado_corregido.xlsx')
