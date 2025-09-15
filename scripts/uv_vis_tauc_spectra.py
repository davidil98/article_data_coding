import os
import pandas as pd
import spectrum_data_loader as sdl
import matplotlib.pyplot as plt
import numpy as np

home = os.path.join('datos_espectros', 'UV-Vis')
file_path = os.path.join(home, 'ngqd_ca_uvvis.txt')

longitud_onda, absorbancia = sdl.load_xy_data(file_path)

data_dic = {
    'Longitud de onda': longitud_onda,
    'Absorbancia': absorbancia
}

df = pd.DataFrame(data_dic)

# ----- Tauc plot data ----
# Para transiciones directas permitidas (común en GQD).
# E(eV) = 1240 / lambda(nm)
df['Energía eV'] = 1240 / df['Longitud de onda']
# Calculamos (A*hν)^n
n = 2
df['Tauc Y'] = (df['Absorbancia'] * df['Energía eV'])**n
# Rango de ajuste lineal
fit_range = df[(df['Energía eV'] > 3.3) & (df['Energía eV'] < 3.5)]
# Regresion lineal
slope, intercept = np.polyfit(fit_range['Energía eV'], fit_range['Tauc Y'], 1)

# Calculamos el band gap (Eg) extrapolando la línea al eje X (donde Y=0)
# y = mx + c  =>  x = -c / m
band_gap = -intercept / slope
fit_line_x = np.linspace(band_gap - 0.1, fit_range['Energía eV'].max(), 100)

fig, axs = plt.subplots(1,2, figsize=(18, 6))

# --- Graph spectrum ----
axs[0].plot(df['Longitud de onda'], df['Absorbancia'], color='green', label='N-GQDs (CA)')

axs[0].set_xlabel('Wavelenght (nm)', fontsize=13)
axs[0].set_xlim([200,550])
axs[0].set_ylabel('Absorbance (a.u.)', fontsize=13)
axs[0].legend(fontsize=12)
axs[0].grid(True, linestyle='--', alpha=0.6)
axs[0].tick_params(axis='x', labelsize=13)
axs[0].tick_params(axis='y', labelsize=13)

# ---- Tauc plot ----
axs[1].plot(df['Energía eV'], df['Tauc Y'], label='N-GQDs (CA)', color='green')
axs[1].set_xlabel(r'Energy (eV, $h\nu$)', fontsize=14)
axs[1].set_ylabel(r'$(\alpha h\nu)^2 \ (u.a.)$', fontsize=14)

axs[1].plot(fit_line_x, slope * fit_line_x + intercept, 'r--', linewidth=2, label='Linear fit')

# Anotar el valor del band gap
axs[1].scatter([band_gap], [0], color='red', s=100, zorder=5) # Marca el punto de Eg
axs[1].annotate(f'$E_g = {band_gap:.2f}$ eV',
             xy=(band_gap, 0),
             xytext=(band_gap - 0.4, max(fit_range['Tauc Y'])*0.5),
             arrowprops=dict(facecolor='black', arrowstyle='->'),
             fontsize=12,
             bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.5))

axs[1].set_xlim([2.6,3.6])
axs[1].set_ylim([-5,50])
axs[1].grid(True, linestyle='--', alpha=0.6)
axs[1].legend(fontsize=13)

# Set x-axis and y-axis tick labels font size
plt.xticks(fontsize=13)
plt.yticks(fontsize=13)
plt.tight_layout()

output_path = os.path.join('..', 'SI_nitrite_sensor', 'Figures', 'uv_vis_tauc_plot.png')
plt.savefig(output_path, dpi=300)

plt.show()