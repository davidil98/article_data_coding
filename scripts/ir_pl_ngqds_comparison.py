from code_functions.data_txt_pull import data_pull
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np # Necesitamos numpy para el error estándar
import matplotlib.image as mpimg

def plot_ir(axs):
    folder = os.path.join('datos_espectros', 'FT-IR')
    file_name_list = ['N-GQD_CA_BLC.txt', 'N-GQD_BC_BLC.txt', 'N-GQD_Glu_BLC.txt']
    names = ['N-GQD (CA)', 'N-GQD (BC)', 'N-GQD (Glu)']
    
    colors = ['green', 'brown', 'gray', 'yellow']
    n=0

    # Definiciones de regiones para los rectángulos (centro, ancho)
    regiones = {
        'gris': [(2900, 100), (750, 100)],
        'amarillo': [(1650, 100), (1350, 100)],
        'naranja': [(1510, 100), (1090, 100), (900, 90)],
        'azul': [(1010, 50)]
    }

    colores_regiones = {
        'gris': 'gray',
        'amarillo': 'yellow',
        'naranja': 'orange',
        'azul': 'blue'
    }

    for file_name in file_name_list:
        file_path = os.path.join(folder, file_name)
        num_de_onda, transmitancia = data_pull(file_path)
        
        data = {
            'Número de onda': num_de_onda,
            'Transmitancia': transmitancia
        }

        df = pd.DataFrame(data)
        
        axs[n].plot(df[['Número de onda']], df[['Transmitancia']], label=names[n], color=colors[n]) 
        axs[n].set_xlabel('Wavenumber ($\\text{cm}^{-1}$)', fontsize=13) if n==2 else None
        axs[n].set_xlim([4000, 400])
        axs[n].set_ylabel('T (%)', fontsize=13)
        axs[n].legend()
        # Set x-axis tick label font size
        axs[n].tick_params(axis='x', labelsize=13) 
        # Set y-axis tick label font size
        axs[n].tick_params(axis='y', labelsize=13)
        
        # Obtener límites del eje Y
        y0, y1 = axs[n].get_ylim()
        height = y1 - y0
        
        # Añadir rectángulos de color
        alpha = 0.3  # Transparencia
        
        # Gris (Alcanos/aromáticos)
        for centro, ancho in regiones['gris']:
            x = centro - ancho/2
            rect = mpatches.Rectangle(
                (x, y0), 
                ancho, 
                height, 
                facecolor=colores_regiones['gris'], 
                alpha=alpha,
                zorder=1
            )
            axs[n].add_patch(rect)
            # Etiqueta solo para las regiones grises
            axs[n].text(
                centro, y1-23, 'Alkanes/\naromatics',
                ha='center', va='bottom', fontsize=10, color='red'
            )
        
        # Amarillo
        for centro, ancho in regiones['amarillo']:
            x = centro - ancho/2
            rect = mpatches.Rectangle(
                (x, y0), 
                ancho, 
                height, 
                facecolor=colores_regiones['amarillo'], 
                alpha=alpha,
                zorder=1
            )
            axs[n].add_patch(rect)
            axs[n].text(
                centro, y1-20, '-NH',
                ha='center', va='bottom', fontsize=11, color='red'
            )
        
        # Naranja
        for centro, ancho in regiones['naranja']:
            x = centro - ancho/2
            rect = mpatches.Rectangle(
                (x, y0), 
                ancho, 
                height, 
                facecolor=colores_regiones['naranja'], 
                alpha=alpha,
                zorder=1
            )
            axs[n].add_patch(rect)
            axs[n].text(
                centro, y0+20, r'CON$\text{H}_{2}$',
                ha='center', va='bottom', fontsize=7, color='red'
            )
        
        # Azul
        for centro, ancho in regiones['azul']:
            x = centro - ancho/2
            rect = mpatches.Rectangle(
                (x, y0), 
                ancho, 
                height, 
                facecolor=colores_regiones['azul'], 
                alpha=alpha,
                zorder=1
            )
            axs[n].add_patch(rect)
            axs[n].text(
                centro, y1-12, '-COH',
                ha='center', va='bottom', fontsize=11, color='red'
            )
            axs[n].text(0.02, 0.85, 'b)', transform=axs[n].transAxes,
            fontsize=18, fontweight='bold', va='top', ha='left') if n==0 else None

        n += 1

def pl_plot(ax, fig):
    home = os.path.join('datos_espectros', 'PL')
    img_viales = mpimg.imread(os.path.join(home, 'pl_ngqd_viales.png'))
    img_cuveta = mpimg.imread(os.path.join(home, 'pl_ngqd_cuveta.png'))
    colors = ['orange', 'green', 'blue']
    n=0

    folders_dic = {
        'N-GQD (BC)': 'ngqd_bc',
        'N-GQD (CA)': 'ngqd_ca',
        'N-GQD (Glu)': 'ngqd_glu'
    }

    plot_dic = {}

    for ngqd_name, ngqd_folder in folders_dic.items():
        folder_path = os.path.join(home, ngqd_folder)
        # Asegúrate de que la carpeta exista antes de intentar listar archivos
        if not os.path.isdir(folder_path):
            print(f"Advertencia: La carpeta no existe - {folder_path}")
            continue
        
        files_list = os.listdir(folder_path)
        dfs_list = []

        for file_ngqd in files_list:
            file_path = os.path.join(folder_path, file_ngqd)
            longitud_onda, intensidad = data_pull(file_path)
            
            data_dic = {
                'Longitud de onda': longitud_onda,
                'Intensidad': intensidad
            }
            df = pd.DataFrame(data_dic)
            dfs_list.append(df)
        
        if not dfs_list:
            print(f"Advertencia: No se encontraron datos para {ngqd_name}")
            continue

        df_contact = pd.concat(dfs_list)
        
        # Agrupar por longitud de onda para calcular promedio Y desviación estándar
        grouped = df_contact.groupby('Longitud de onda')['Intensidad']
        df_proc = grouped.agg(['mean', 'std', 'count']).reset_index()
        
        # Calcular el error estándar de la media (SEM)
        # SEM = std / sqrt(n)
        df_proc['sem'] = df_proc['std'] / np.sqrt(df_proc['count'])
        
        # Aplicar el promedio móvil sobre la media y rellenar los NaN iniciales
        df_proc['mean_suavizada'] = df_proc['mean'].rolling(window=5, center=True, min_periods=1).mean()

        # Diccionario con datos procesados por tipo de N-GQD
        plot_dic[ngqd_name] = df_proc

    for ngqd_type, ngqd_data in plot_dic.items():
        # Extraer datos para graficar
        x = ngqd_data['Longitud de onda']
        y_suavizada = ngqd_data['mean_suavizada']
        error = ngqd_data['std'] # O puedes usar 'sem' para un error más pequeño

        # Graficar la línea del promedio suavizado
        ax.plot(x, y_suavizada, label=ngqd_type, linewidth=2, color=colors[n])
        
        # Añadir la banda de error sombreada (desviación estándar)
        ax.fill_between(x, y_suavizada - error, y_suavizada + error, alpha=0.2, color=colors[n])
        n+=1

    # Estilo y etiquetas
    ax.set_xlabel('Wavelength (nm)', fontsize=13)
    ax.set_xlim([300, 680])
    ax.set_ylim(bottom=-50)
    ax.set_ylabel('Intensity (a.u.)', fontsize=13)
    #ax.set_title('Espectros de PL Promedio con Banda de Error', fontsize=14)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.text(0.02, 0.95, 'a)', transform=ax.transAxes,
            fontsize=18, fontweight='bold', va='top', ha='left')
    # Change the font size of axis tick labels
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)

    # anotaciones
    ax.annotate('Ex',
                xy=(385, 735),
                horizontalalignment='center',
                verticalalignment='bottom',
                xytext=(400, 900),
                arrowprops=dict(arrowstyle='fancy, head_length=0.4, head_width=0.4, tail_width=0.4', color='k')
                )

    ax.annotate('Em (395nm-650nm)',
                xy=(455, 2200),
                horizontalalignment='center',
                verticalalignment='bottom',
                xytext=(455, 2300),
                arrowprops=dict(arrowstyle='-[, widthB=8, lengthB=1, angleB=0', lw=1))

    # --- 3. AÑADIR IMÁGENES INCRUSTADAS (INSETS) ---
    # Posición y tamaño del primer recuadro para la imagen [izquierda, abajo, ancho, alto]
    # en coordenadas de la figura (0 a 1)
    ax_inset1 = fig.add_axes([0.70, 0.60, 0.25, 0.25])
    ax_inset1.imshow(img_cuveta)
    ax_inset1.axis('off') # Ocultar los ejes del recuadro

    # Posición y tamaño del segundo recuadro
    ax_inset2 = fig.add_axes([0.70, 0.37, 0.25, 0.25])
    ax_inset2.imshow(img_viales)
    ax_inset2.axis('off')

if __name__ == '__main__':
    fig = plt.figure(layout='constrained', figsize=(15,7))
    subfigs = fig.subfigures(1,2)

    ax_left = subfigs[0].subplots(1,1)
    pl_plot(ax_left, fig=subfigs[0])

    ax_right = subfigs[1].subplots(3,1, sharex=True)
    plot_ir(ax_right)

    output_path = os.path.join('..', 'nitrite_sensor_acsomega_article', 'Figures', 'ir_pl_comparison_ngqds.png')
    plt.savefig(output_path, dpi=300)
    plt.show()