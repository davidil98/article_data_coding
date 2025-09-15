import spectrum_data_loader as sdl
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.image as mpimg
from scipy.stats import linregress

# --- 1. LECTURA Y PROCESAMIENTO DE DATOS ---
home = os.path.join('datos_espectros', 'PL', 'ngqd_ca_curva_PerkinElmer')
file_name_list = os.listdir(home)

plot_dic = {}
max_int_dic = {}

# <<< CAMBIO: Leemos cada archivo como una única medición.
for file_name in file_name_list:
    # Extraer la concentración del nombre del archivo
    try:
        conc_num = int(file_name.replace('uM.txt', ''))
        file_path = os.path.join(home, file_name)
        
        # Leer los datos del espectro
        longitud_onda, intensidad = sdl.load_xy_data(file_path)
        df = pd.DataFrame({'Wavelength': longitud_onda, 'Intensity': intensidad})
        # Encontrar la intensidad máxima en el rango de emisión
        df_filtered = df[(df['Wavelength'] >= 395) & (df['Wavelength'] <= 650)]

        # Guardar el espectro completo para graficar
        plot_dic[conc_num] = df

    except ValueError:
        print(f"Omitiendo archivo no válido: {file_name}")


# --- 2. CÁLCULOS PARA CURVAS DE CALIBRACIÓN ---
# Ordenar los datos por concentración
concentrations_num = sorted(max_int_dic.keys())
F_values = np.array([max_int_dic[c] for c in concentrations_num])
F0 = max_int_dic[0] # Intensidad del blanco (0 µM)

# Para el gráfico de Stern-Volmer
sv_y_ratio = F0 / F_values
# Rango lineal para el ajuste (excluyendo 100 uM)
linear_range_mask = np.array(concentrations_num) < 100
x_fit = np.array(concentrations_num)[linear_range_mask]

# Rango lineal y ajuste de Stern-Volmer
y_fit_sv = sv_y_ratio[linear_range_mask]
slope_sv, intercept_sv, r_value_sv, _, _ = linregress(x_fit, y_fit_sv)
K_sv = slope_sv

# Ajuste de la curva de calibración simple para el LOD
y_fit_simple = F_values[linear_range_mask]
slope_simple, intercept_simple, r_value_simple, _, _ = linregress(x_fit, y_fit_simple)
m = abs(slope_simple)

# --- 3. CREACIÓN DE GRÁFICOS ---
fig, axs = plt.subplots(1, 3, figsize=(18, 5.5))

# --- Gráfico a) Espectros de Emisión ---
for conc in sorted(plot_dic.keys()):
    df_plot = plot_dic[conc]
    axs[0].plot(df_plot['Wavelength'], df_plot['Intensity'], label=f'{conc} µM', linewidth=2)

axs[0].set_xlabel('Wavelength (nm)', fontsize=13)
axs[0].set_xlim([390, 650])
axs[0].set_ylim([-5, 100])
axs[0].set_ylabel('Intensity (a.u.)', fontsize=13)
axs[0].legend(title=r'[$\text{NO}_{2}^{-}$]', fontsize=9, loc='upper right')
axs[0].grid(True, linestyle='--', alpha=0.6)

# --- Gráfico b) Curva de Calibración (Intensidad vs. Conc.) ---
# Usamos scatter plot porque no hay barras de error por réplica.
axs[1].plot(concentrations_num, F_values, 'o', color='b', label='Experimental data')
axs[1].plot(x_fit, slope_simple * x_fit + intercept_simple, 'r--', label='Linear fit')
text_simple = (f'$y = {slope_simple:.2f}x + {intercept_simple:.2f}$\n'
               f'$R^2 = {r_value_simple**2:.4f}$')
axs[1].text(0.6, 0.7, text_simple, transform=axs[1].transAxes, fontsize=11, bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))
axs[1].set_xlabel(r'[$\text{NO}_{2}^{-}$] (µM)', fontsize=13)
axs[1].set_ylabel('Intensity (a.u.)', fontsize=13)
axs[1].legend()
axs[1].grid(True, linestyle='--', alpha=0.6)

# --- Gráfico c) Gráfico de Stern-Volmer ---
# Usamos scatter plot.
axs[2].plot(concentrations_num, sv_y_ratio, 'o', color='g', label='Experimental data')
axs[2].plot(x_fit, slope_sv * x_fit + intercept_sv, 'r--', label='Linear fit')
text_sv = (f'$F_0/F = {K_sv:.4f}' + r'[\text{NO}_{2}^{-}]' + f' + {intercept_sv:.4f}$\n'
           f'$R^2 = {r_value_sv**2:.4f}$\n'
           f"$K_{{sv}} = {K_sv:.4f}$ L/µmol")
axs[2].text(0.5, 0.15, text_sv, transform=axs[2].transAxes, fontsize=11, bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))
axs[2].set_xlabel(r'[$\text{NO}_{2}^{-}$] (µM)', fontsize=13)
axs[2].set_ylabel('$F_0 / F$', fontsize=13)
axs[2].legend()
axs[2].grid(True, linestyle='--', alpha=0.6)

# --- 4. FINALIZACIÓN Y GUARDADO ---
etiquetas = ['a)', 'b)', 'c)']
for ax, etiqueta in zip(axs, etiquetas):
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.text(-0.1, 1.05, etiqueta, transform=ax.transAxes, fontsize=16, fontweight='bold', va='top', ha='right')

fig.tight_layout()

output_path = os.path.join('..', 'SI_nitrite_sensor', 'Figures', 'calibration_curve_perkin_elmer.png')
plt.savefig(output_path, dpi=300)

plt.show()