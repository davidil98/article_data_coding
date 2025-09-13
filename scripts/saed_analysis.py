import os
import pandas as pd

folder_path = os.path.join('..', 'Datos', 'TEM_analysis', 'SAED')
file_path = os.path.join(folder_path, 'Glu_diffraction_patterns.csv')

df = pd.read_csv(file_path)

# 'Major' contiene el diámetro del anillo de difracción en el espacio recíproco (unidades: nm⁻¹)
reciprocal_diameter = df['Major'] 

# Se calcula el radio en el espacio recíproco (g = 1/d)
# g (nm⁻¹) = diametro_reciproco / 2
reciprocal_spacing = reciprocal_diameter / 2

# Se calcula el espaciado d en nanómetros
# d (nm) = 1 / g (nm⁻¹)
d_spacing_nm = 1 / reciprocal_spacing

# Se convierte el espaciado d de nanómetros (nm) a Angstroms (Å)
d_spacing_A = d_spacing_nm * 10

print("Los espaciados d calculados en Angstroms (Å) son:")
print(d_spacing_A)