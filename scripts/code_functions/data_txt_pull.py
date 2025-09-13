def data_pull(txt_file):
    #print('Archivo:', txt_file)
    # Lista de protocolos de codificación a probar
    protocols = ['utf-8', 'latin-1', 'ANSI']  # 'latin-1' es más robusto que 'ANSI'
    separadores = [' ', '\t', '  ']  # Separadores comunes
    
    # Intentar abrir el archivo con diferentes protocolos de codificación
    lines = None
    for protocol in protocols:
        try:
            with open(txt_file, 'r', encoding=protocol) as f:
                lines = f.readlines()
            #print(f'Archivo leído con el protocolo: {protocol}')
            break
        except UnicodeDecodeError:
            continue
    # Si no se pudo leer el archivo, salir con un mensaje de error
    if lines is None:
        print('Error: No se pudo leer el archivo. Verifica el protocolo de codificación.')
    
    # Inicializar listas para almacenar los datos
    x_data = []
    y_data = []
    
    # Determinar el separador de columnas
    separador = None
    for line in lines:
        if not line.strip():  # Saltar líneas vacías
            continue
        
        # Buscar el separador si aún no se ha determinado
        if separador is None:
            for sep in separadores:
                parts = line.split(sep)
                if len(parts) >= 2:
                    try:
                        float(parts[0].replace(',', '.'))
                        float(parts[1].replace(',', '.'))
                        separador = sep
                        #print(f'Separador detectado: "{separador}"')
                        break
                    except ValueError:
                        continue
        # Si no se encontró un separador válido, continuar con la siguiente línea
        if separador is None:
            continue

        # Procesar la línea
        try:
            parts = line.split(separador)
            x_val = float(parts[0].replace(',', '.'))
            y_val = float(parts[1].replace(',', '.'))
            x_data.append(x_val)
            y_data.append(y_val)
        except (ValueError, IndexError):
            continue  # Saltar líneas con formato inválido

    # Verificar si se extrajeron datos
    if not x_data or not y_data:
        print('Error: No se pudieron extraer datos. Verifica el formato del archivo.')
        
    return x_data, y_data