import matplotlib.pyplot as plt
import os
import pandas as pd
from code_functions.data_txt_pull import data_pull

home = os.path.join('datos_espectros', 'FT-IR')
data_files = {
    'N-GQD_CA_BLC.txt': ['Citric_Acid.csv', 'EDA.csv'],
    'N-GQD_BC_BLC.txt': ['Black_Carbon.csv', 'EDA.csv'],
    'N-GQD_Glu_BLC.txt': ['D_glucosa.csv', 'Hexadecilamina.csv']
}

fig, axs = plt.subplots(3,1, layout='constrained', figsize=(10,6))
ngqd_names = [f'N-GQDs {precursor}' for precursor in ['(CA)', '(BC)', '(Glu)']]
n = 0

for ngqd_file, precursores_files in data_files.items():
    file_path_ngqd = os.path.join(home, ngqd_file)
    num_onda, transmitancia = data_pull(file_path_ngqd)
    data = {
        'Número de onda': num_onda,
        'Transmitancia': transmitancia
    }
    df = pd.DataFrame(data)
    # graficar los tipos de N-GQD
    axs[n].plot(df['Número de onda'], df['Transmitancia'], label = ngqd_names[n], color='black')
    axs[n].set_xlabel('Wavenumber ($\\text{cm}^{-1}$)', fontsize=13)
    axs[n].set_xlim([4000, 1000])
    axs[n].set_ylabel('T (%)', fontsize=13)
    # Set x-axis tick label font size
    axs[n].tick_params(axis='x', labelsize=13) 
    # Set y-axis tick label font size
    axs[n].tick_params(axis='y', labelsize=13)

    # graficar los precursores
    for precursor_file in precursores_files:
        precursor_file_path = os.path.join(home, precursor_file)
        df_precursor = pd.read_csv(precursor_file_path)
        df_precursor.columns = ['Número de onda', 'Transmitancia']
        axs[n].plot(df_precursor['Número de onda'], df_precursor['Transmitancia'], label=precursor_file.split('.')[0].replace('_', ' '))
    
    axs[n].legend()
    n += 1

output_route = (os.path.join('..', 'SI_nitrite_sensor', 'Figures', 'ir_ngqd_precursores.png'))
plt.savefig(output_route, dpi=300, bbox_inches='tight')
plt.show()