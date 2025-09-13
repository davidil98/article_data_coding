from code_functions.data_txt_pull import data_pull
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.image as mpimg
import matplotlib.patches as mpatches

def plot_pl_time(ax):
    folder = os.path.join('datos_espectros', 'PL', 'ngqd_ca_tiempo_interaccion')
    files_list = os.listdir(folder)
    img_path = os.path.join('datos_espectros', 'PL', "PL_interaccionNO_cuali.jpg")
    img_interractionNO = mpimg.imread(img_path)

    time_read_labels = [f'{str(n)} s' for n in np.arange(0, 121, 30)]
    n=0

    for file_name in files_list:
        file_path = os.path.join(folder, file_name)

        longitud_onda, intensidad = data_pull(file_path)

        data_dic = {
            'Longitud de onda': longitud_onda,
            'Intensidad': intensidad
        }

        df = pd.DataFrame(data_dic)

        ax.plot(df['Longitud de onda'], df['Intensidad'], label=time_read_labels[n])
        
        n+=1

    # --- GRAFICO DE LINEAS ---
    ax.set_xlabel('Wavelength (nm)', fontsize=13)
    ax.set_xlim([300,750])
    ax.set_ylabel('Intensity (a.u.)', fontsize=13)
    ax.set_ylim(bottom=-10)
    ax.legend(title='Time lecture')
    ax.grid(True, linestyle = '--', alpha=0.6)
    ax.text(0.02, 0.95, 'a)', transform=ax.transAxes,
            fontsize=18, fontweight='bold', va='top', ha='left')

    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)

    # Posición y tamaño para la imagen [izquierda, abajo, ancho, alto] en coordenadas de la figura (0 a 1)
    ax_inset = ax.inset_axes([0.65, 0.4, 0.3, 0.3])
    ax_inset.imshow(img_interractionNO)
    ax_inset.axis('off')

def plot_ir_nitrites (axs):
    home = os.path.join('datos_espectros', 'FT-IR')
    files = ['N-GQD_CA_BLC.txt', 'N-GQD_CA_pH3_BLC.txt', 'N-GQD_CA_NO2_BLC.txt']
    names = ['N-GQDs (CA)', 'N-GQDs (CA), pH 3', r'N-GQDs (CA) + $\text{NO}_{2}^{-}$']

    colors = ['green', 'brown', 'blue']
    n=0

    # regiones de rectángulos, valor: tupla (centro, ancho)
    regiones = {
        'yellow': (1600, 200), # imina y amina II
        'brown': (1300, 250), # aminas aromáticas
        'purple': (1040, 250) # aminas alifáticas
    }

    for file in files:
        file_path = os.path.join(home, file)
        num_de_onda, transmitancia = data_pull(file_path)
        
        data = {
            'Número de onda': num_de_onda,
            'Transmitancia': transmitancia
        }

        df = pd.DataFrame(data)

        axs[n].plot(df[['Número de onda']], df[['Transmitancia']], label=names[n], color=colors[n]) 
        axs[n].set_xlabel('Wavenumber ($\\text{cm}^{-1}$)', fontsize=15) if n==2 else None
        axs[n].set_xlim([4000, 400])
        axs[n].set_ylabel('T (%)', fontsize=15)
        axs[n].legend()
        # Set x-axis tick label font size
        axs[n].tick_params(axis='x', labelsize=14) 
        # Set y-axis tick label font size
        axs[n].tick_params(axis='y', labelsize=14)
        axs[n].text(0.02, 0.85, 'b)', transform=axs[n].transAxes,
            fontsize=18, fontweight='bold', va='top', ha='left') if n==0 else None
        
        y0, y1 = axs[n].get_ylim()
        height = y1 - y0  # Altura max de cada fig de espectro
        alpha = 0.3  # alfa para los rectángulos

        for color, region in regiones.items():
            centro, ancho = region[0], region[1]
            x = centro - ancho/2

            rect = mpatches.Rectangle(
                (x, y0),
                ancho,
                height,
                facecolor=color,
                alpha=alpha,
                zorder=1
            )
            axs[n].add_patch(rect)
        n+=1

# ------------- MAIN configuration -------------
fig = plt.figure(layout='constrained', figsize=(15,6))
subfigs = fig.subfigures(1,2)

ax_left = subfigs[0].subplots(1,1)
plot_pl_time(ax_left)

ax_right = subfigs[1].subplots(3,1, sharex=True)
plot_ir_nitrites(ax_right)

output_path = os.path.join('..', 'nitrite_sensor_acsomega_article', 'Figures', 'plTime_irNitrites_spectra.png')
plt.savefig(output_path, dpi=300)

plt.show()