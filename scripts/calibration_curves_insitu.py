from code_functions.data_txt_pull import data_pull
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.image as mpimg
from scipy.stats import linregress

# --- 1. LECTURA Y PROCESAMIENTO DE DATOS ---
home = os.path.join('datos_espectros', 'PL', 'ngqd_ca_curva_in_situ', 'ensayo1a16')
folders_names_list = os.listdir(home)

plot_dic = {}
max_int_em_dic = {}
std_int_em_dic = {}

for folder_name in folders_names_list:
    folder_path = os.path.join(home, folder_name)
    file_name_list = os.listdir(folder_path)
    dfs_list, max_int_em_list = [], []

    for file_name in file_name_list:
        file_path = os.path.join(folder_path, file_name)
        longitud_onda, intensidad = data_pull(file_path)
        df = pd.DataFrame({'Longitud de onda': longitud_onda, 'Intensidad': intensidad})
        dfs_list.append(df)
        df_filtered_em = df[(df['Longitud de onda'] >= 395) & (df['Longitud de onda'] <= 650)]
        max_int_em_list.append(df_filtered_em['Intensidad'].max())
    
    df_concat = pd.concat(dfs_list)
    grouped = df_concat.groupby('Longitud de onda')['Intensidad']
    df_proc = grouped.agg(['mean', 'std', 'count']).reset_index()
    df_proc['mean_suavizada'] = df_proc['mean'].rolling(window=5, center=True, min_periods=1).mean()

    conc_label = folder_name.replace('uM', r' µM')
    plot_dic[conc_label] = df_proc
    max_int_em_dic[conc_label] = np.mean(max_int_em_list)
    std_int_em_dic[conc_label] = np.std(max_int_em_list)

# --- 2. CÁLCULOS PARA CURVAS DE CALIBRACIÓN ---
concentrations_str_unsorted = list(max_int_em_dic.keys())
# Extraer número, convertir a int, ordenar y luego reformatear a string
concentrations_num = sorted([int(s.split(' ')[0]) for s in concentrations_str_unsorted])
concentrations_str = [str(c) + r' µM' for c in concentrations_num]

F_means = np.array([max_int_em_dic[s] for s in concentrations_str])
F_stds = np.array([std_int_em_dic[s] for s in concentrations_str])
F0_mean = F_means[0]
F0_std = F_stds[0]

# Para el gráfico de Stern-Volmer
sv_y_ratio = F0_mean / F_means
relative_error = np.sqrt((F0_std / F0_mean)**2 + (F_stds / F_means)**2)
sv_y_error = sv_y_ratio * relative_error

# Rango lineal y ajuste de Stern-Volmer (hasta 100 µM)
linear_range_mask = np.array(concentrations_num) <= 100
x_fit = np.array(concentrations_num)[linear_range_mask]
y_fit_sv = sv_y_ratio[linear_range_mask]
slope_sv, intercept_sv, r_value_sv, _, _ = linregress(x_fit, y_fit_sv)
K_sv = slope_sv

# Ajuste de la curva de calibración simple para el LOD
y_fit_simple = F_means[linear_range_mask]
slope_simple, intercept_simple, r_value_simple, _, _ = linregress(x_fit, y_fit_simple)
m = abs(slope_simple)
sigma_blanco = F0_std
lod = (3 * sigma_blanco) / m

# --- 3. CREACIÓN DE GRÁFICOS ---
fig, axs = plt.subplots(1, 3, figsize=(18, 5.5))

# --- Gráfico a) Espectros de Emisión ---
for conc_label, plot_data in plot_dic.items():
    axs[0].plot(plot_data['Longitud de onda'], plot_data['mean_suavizada'], label=conc_label, linewidth=2)
    axs[0].fill_between(plot_data['Longitud de onda'], plot_data['mean_suavizada'] - plot_data['std'], plot_data['mean_suavizada'] + plot_data['std'], alpha=0.2)

img_path = os.path.join('datos_espectros', 'PL', 'pl_photo_1a16essay.jpg')
img_calibration_curve = mpimg.imread(img_path)

axs[0].set_xlabel('Wavelength (nm)', fontsize=13)
axs[0].set_xlim([390, 700])
axs[0].set_ylim([-10, 2000])
axs[0].set_ylabel('Intensity (a.u.)', fontsize=13)
axs[0].legend(title=r'[$\text{NO}_{2}^{-}$]', fontsize=9)
axs[0].grid(True, linestyle='--', alpha=0.6)

# Posición y tamaño para la imagen [izquierda, abajo, ancho, alto] en coordenadas de la figura (0 a 1)
ax_inset = axs[0].inset_axes([0.65, 0.2, 0.3, 0.3])
ax_inset.imshow(img_calibration_curve)
ax_inset.axis('off')

# --- Gráfico b) Curva de Calibración (Intensidad vs. Conc.) ---
axs[1].errorbar(concentrations_num, F_means, yerr=F_stds, fmt='o', color='b', ecolor='lightgray', elinewidth=3, capsize=5, label='Experimental data')
axs[1].plot(x_fit, slope_simple * x_fit + intercept_simple, 'r--', label='Linear fit')
text_simple = (f'$y = {slope_simple:.2f}x + {intercept_simple:.2f}$\n'
               f'$R^2 = {r_value_simple**2:.4f}$\n'
               f'LOD = {lod:.2f} µM')
axs[1].text(0.05, 0.2, text_simple, transform=axs[1].transAxes, fontsize=11, bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))
axs[1].set_xlabel(r'[$\text{NO}_{2}^{-}$] (µM)', fontsize=13)
axs[1].set_ylabel('Intensity (a.u.)', fontsize=13)
axs[1].legend()
axs[1].grid(True, linestyle='--', alpha=0.6)

# --- Gráfico c) Gráfico de Stern-Volmer ---
axs[2].errorbar(concentrations_num, sv_y_ratio, yerr=sv_y_error, fmt='o', color='g', ecolor='lightgray', elinewidth=3, capsize=5, label='Experimental data')
axs[2].plot(x_fit, slope_sv * x_fit + intercept_sv, 'r--', label='Linear fit')
text_sv = (f'$F_0/F = {K_sv:.3f}' + r' [\text{NO}_{2}^{-}]' + f'+ {intercept_sv:.3f}$\n'
           f'$R^2 = {r_value_sv**2:.4f}$\n'
           f"$K_{{sv}} = {K_sv:.4f}$ L/µmol")
axs[2].text(0.05, 0.65, text_sv, transform=axs[2].transAxes, fontsize=11, bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))
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

output_path = os.path.join('..', 'nitrite_sensor_acsomega_article', 'Figures', 'calibration_curve_series.png')
plt.savefig(output_path, dpi=300)

plt.show()