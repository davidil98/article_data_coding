import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.image as mpimg
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from code_functions.data_txt_pull import data_pull

# --- FUNCIÓN 1: GRÁFICO DE EFECTO DE LAMBDA DE EXCITACIÓN ---
def plot_lambda_ex(ax):
    """
    Genera el gráfico de espectros de PL variando la longitud de onda de excitación.
    """
    folder = os.path.join('datos_espectros', 'PL', 'ngqd_ca_lamda_ex')
    if not os.path.isdir(folder):
        ax.text(0.5, 0.5, f"Error: La carpeta no existe\n{folder}", ha='center', va='center')
        return

    files_list = sorted(os.listdir(folder))
    lambda_ex_list = [350, 365, 380, 395, 410, 425]
    
    # Configuración del degradado de color
    norm = mcolors.Normalize(vmin=min(lambda_ex_list), vmax=max(lambda_ex_list))
    cmap = cm.get_cmap('plasma')

    for n, file_name in enumerate(files_list):
        if n < len(lambda_ex_list): # Asegurarse de no exceder la lista de lambdas
            file_path = os.path.join(folder, file_name)
            longitud_onda, intensidad = data_pull(file_path)
            
            color_ex = cmap(norm(lambda_ex_list[n]))
            ax.plot(longitud_onda, intensidad, 
                    label=f"{lambda_ex_list[n]} nm", 
                    color=color_ex)

    # Estilo y etiquetas
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Intensity (a.u.)')
    ax.set_xlim([300, 700])
    ax.set_ylim(bottom=-10)
    ax.legend(title=r'$\lambda_{ex}$')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.text(0.02, 0.95, 'a)', transform=ax.transAxes,
            fontsize=15, fontweight='bold', va='top', ha='left')

# --- FUNCIÓN 2: GRÁFICO DE DILUCIONES ---
def plot_dilutions(ax):
    """
    Genera el gráfico de espectros de PL para diferentes diluciones de la muestra.
    """
    home = os.path.join('datos_espectros', 'PL', 'ngqd_ca_dilutions')
    if not os.path.isdir(home):
        ax.text(0.5, 0.5, f"Error: La carpeta no existe\n{home}", ha='center', va='center')
        return
        
    img_path = os.path.join(home, 'pl_dilutions_photo.png')
    img_dilutions = mpimg.imread(img_path) if os.path.exists(img_path) else None

    folders_data_dic = {
        'concentrated (20 mg/mL)': 'conc', r'1:1': '1 a 1', r'1:2': '1 a 2',
        r'1:4': '1 a 4', r'1:8': '1 a 8', r'1:16': '1 a 16'
    }
    plot_dic = {}

    for concentration_number, data_folder_name in folders_data_dic.items():
        folder_path = os.path.join(home, data_folder_name)
        if not os.path.isdir(folder_path): continue
        
        dfs_list = [pd.DataFrame(zip(*data_pull(os.path.join(folder_path, fn))), columns=['Longitud de onda', 'Intensidad']) for fn in os.listdir(folder_path)]
        if not dfs_list: continue

        df_concat = pd.concat(dfs_list)
        grouped = df_concat.groupby('Longitud de onda')['Intensidad']
        df_proc = grouped.agg(['mean', 'std', 'count']).reset_index()
        df_proc['mean_suavizada'] = df_proc['mean'].rolling(window=5, center=True, min_periods=1).mean()
        plot_dic[concentration_number] = df_proc

    colors_list = ['blue', 'orange', 'green', 'red', 'purple', 'brown']
    for n, (conc_number, plot_data) in enumerate(plot_dic.items()):
        x = plot_data['Longitud de onda']
        y_suavizada = plot_data['mean_suavizada']
        error = plot_data['std']
        ax.plot(x, y_suavizada, label=conc_number, linewidth=2, color=colors_list[n])
        ax.fill_between(x, y_suavizada - error, y_suavizada + error, alpha=0.2, color=colors_list[n])

    # Estilo y etiquetas
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Intensity (a.u.)')
    ax.set_xlim([325, 700])
    ax.set_ylim(bottom=-10)
    ax.legend(title='Dilution Factor')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.text(0.02, 0.95, 'b)', transform=ax.transAxes,
            fontsize=15, fontweight='bold', va='top', ha='left')

    # Insertar imagen si existe
    if img_dilutions is not None:
        ax_inset = ax.inset_axes([0.65, 0.2, 0.3, 0.3])
        ax_inset.imshow(img_dilutions)
        ax_inset.axis('off')

# --- FUNCIÓN 3: GRÁFICOS DE EFECTO DEL PH ---
def plot_ph_effects(ax_line, ax_bar):
    """
    Genera el gráfico de espectros de PL y el de barras de intensidad máxima
    variando el pH de la solución.
    """
    folder = os.path.join('datos_espectros', 'PL', 'ngqd_ca_pH_soln1a4')
    if not os.path.isdir(folder):
        ax_line.text(0.5, 0.5, f"Error: La carpeta no existe\n{folder}", ha='center', va='center')
        ax_bar.text(0.5, 0.5, "", ha='center', va='center')
        return

    files_list = sorted(os.listdir(folder))
    pH_nums = [2, 3, 4, 6, 7, 8, 10]
    max_int_em_dic = {}

    # Configuración del degradado de color
    norm = mcolors.Normalize(vmin=min(pH_nums), vmax=max(pH_nums))
    cmap = cm.get_cmap('coolwarm_r')

    # --- Gráfico de líneas (ax_line) ---
    for n, file_name in enumerate(files_list):
        if n < len(pH_nums):
            file_path = os.path.join(folder, file_name)
            longitud_onda, intensidad = data_pull(file_path)
            df = pd.DataFrame({'Longitud de onda': longitud_onda, 'Intensidad': intensidad})
            
            current_ph = pH_nums[n]
            color_ph = cmap(norm(current_ph))
            ax_line.plot(df['Longitud de onda'], df['Intensidad'], label=f"pH {current_ph}", color=color_ph)
            
            df_filtered_em = df[(df['Longitud de onda'] >= 380) & (df['Longitud de onda'] <= 700)]
            max_int_em_dic[current_ph] = df_filtered_em['Intensidad'].max()

    ax_line.set_xlabel('Wavelength (nm)')
    ax_line.set_ylabel('Intensity (a.u.)')
    ax_line.legend()
    ax_line.set_xlim([350, 700])
    ax_line.set_ylim(bottom=-10, top=400)
    ax_line.grid(True, linestyle='--', alpha=0.6)
    ax_line.text(0.02, 0.95, 'c)', transform=ax_line.transAxes,
            fontsize=15, fontweight='bold', va='top', ha='left')

    # --- Gráfico de barras (ax_bar) ---
    sorted_items = sorted(max_int_em_dic.items())
    labels = [str(item[0]) for item in sorted_items]
    max_int_em_values = [item[1] for item in sorted_items]
    bar_colors = [cmap(norm(float(ph))) for ph in labels]

    ax_bar.bar(labels, max_int_em_values, color=bar_colors, edgecolor='black')
    ax_bar.set_xlabel('pH')
    ax_bar.set_ylabel('Max. Intensity (a.u.)')
    ax_bar.text(0.02, 0.95, 'd)', transform=ax_bar.transAxes,
            fontsize=15, fontweight='bold', va='top', ha='left')


# --- EJECUCIÓN PRINCIPAL ---
if __name__ == '__main__':
    # Cargamos lienzo principal con una cuadrícula de 2x2
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    # Llamar a cada función para que dibuje en el eje ('ax') correspondiente
    plot_lambda_ex(axs[0, 0])
    plot_dilutions(axs[0, 1])
    plot_ph_effects(axs[1, 0], axs[1, 1])

    # Ajustar el layout para evitar solapamientos y guardar la figura
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    output_path = os.path.join('..', 'nitrite_sensor_acsomega_article', 'Figures', 'pl_ngqd_ca_effects_combined.png')
    plt.savefig(output_path, dpi=300)

    # Mostrar el gráfico
    plt.show()