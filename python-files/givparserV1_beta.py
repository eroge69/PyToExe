import os
import re
import pdfplumber

print("\033[92m")  # ANSI verde claro (lime green)

print(r"""                                                                                                                                                                 
                                          .+*##%%@@@@%@@@@@%%##*+=                                       
                                     .+#%%#%@+*%-*@@*-=%@%==++%@#%@%#+-                                  
                                  +#%@@+---*@==@=+@%---*@#----%#-===%%%%#+                               
                               +%@@@@@@+-==-%+-+-=@==*+-%+-%+=@+=@==@*-%@@%%+                            
                            =#%@@@@@@@@%-==+#%###%%%%%%%%%#@##%===-*%-*@%*-=@@#=                         
                          +%@@@@@@@@@@@@%%%%#**+++++++=+++++++*#%%%@*=%*---=@@@@%+                       
                        =%@@@@@@@@@@@@%##+++++====---------=---=+=++#%%*##-+@@@@@@%+                     
                      -#@@@@@@@@@@@%#+++===--------------------------+*#%@##@@@@@%*%%=                   
                     *@@@@@@@@%###*++==***+-=*+--------------------:-===-+#%@@@%*-=-*%*                  
                   -%@@@@@@@@@%*****====*+#%*==++--------==+++++++=--::::-=+#%@*-*@%+%@%=                
                  +%@@@@@@@@@#+===-=+*#*##***##+=+----=+**+======++*+*+-::-+==*%#-*@%*-#@+               
                 *@@@@@@@@%#++=-------=###%%#*+##*+==+*###+++++++++++=+++=:::--+%%%*-+#%*%#              
                #@@@@@@@@%#++***##***++###***#%######*+*+=--=------==+**=*+-::=++*%*#@%=-%@#             
               #@@@@@@@@%++=------==++*##%%%##%%%%######+=-+++=-----==-=+=**=::-+++%@%=-**+%#            
              *@@@@@%@@%++=------=====+++**##%%###%%####%##*++++--=+*++=-+*+*=::-=++%%==+*#%@#           
             +@@%#**+*#++=--=+***********#%####%%%%%*%#####%#*++=-==+++*==++=*=::-=++%@@@%*==@*          
            -%@@#*=*++*==-------=+*#**+=-=+**##*#+#%%*%#%=#%%%#**=+++++++=+*+=*-:::=++%@+-+#%%%=         
            #@@@%#======------=-----==++***##%##*+*%%%*%#+*#%####%*==+++++++*=*=:::-+++%%%#+-=#%.        
           +@@#==#@@*+=------+=+++*#####%%%%%%*%#++%%%###**#%%%#%%**====++++*+++--::-++*@%-+%@@@+        
          .%@@#---#%+=--------==+**#%%%%######%%##**+*+*#*%%%*###%####++++=+*=*+-----=++#@*-%@@@%:       
          =@@@=----=+==------*******+***######**+****##%*%#%#%##%%%*#*#=+==+*+*+------+=+%@%@@@@@+       
          #@@@#=*------=--------+########*******##%%%*%*%%%%#%##%#####++++++#=*=------=++#@@@@@@@%       
         :%@@@@@@%--:-:::-------===++=--=**##%###**#*%#%%#*#%##%%%*##%+++++****--------++*@@@@@@@@-      
         =@@@@@@@@=-----::--------------+%#%%#%%%%%*#**%%%%#####%#*#*#*+==*#**=--------=++%@@@@@@@=      
         +@@@@@@%==*=----::-------------+%%%#####%%#%*##%%%#*-*%%%%**+*==*###+---------=++%@@@@@@@*      
         *@@@@@#=*==-=----::------------=*####%#%%%#%%*##%%%#*-#%%%#%*++*+**=----------=++#@@@@@@@#      
         *@@@@#+%#==:-==--::--------=-----%#%##%#%%%#%%*#%%%##=-##%####+**+=------------+=#@@@@@@@#      
         #@@@@%@@#==:::--:-+#+------------=+*##%%###%*%##%##%##==%%%%##%#*+=------------++#@@@@@@@#.     
         *@@@@@@@#==::::::=##%+------------=*#########*#**###%#######%%%%%###*+=-------=++#@@@@@@@#      
         +@@@@@@@%=+:::::::+++=:--==--------+#%##%#%%#####**#############%%#%**#*=-----=++#@@@@@@@*      
         =@@@@@@@%++-:::::::--:::--+**++=-----==-*%###%#######*####*##*#%%###%*+##*=---+++%@@@@@@@+      
         :%@@@@@@@+==:::::::-=++++=-------------=#%%%#*#%######%******%%#%##%%**#%##*--++*@@@@@@@@-      
          #@@@@@@@#=+::::::::::::-=++++=------=--+%%###%%%#%#####%%%%%#%%%%##****%#**+=++#@@@@@@@%.      
          +@@@@@@@%++-:::::::::::::-+=--+++++-----#%%%%%#%###%#%#+++#%*##%%*--==+*+*%*+++%@@@@@@@*       
          :%@@@@@@@#=+:::::::::::::=%#------=-----+*##%########%#%%%%%*%%#=--------=#%*+#@@@@@@@%-       
           +@@@@@@@@+==:::::::::::::-:::--+*+++++++++++*%%%######%#*%%*%#=----------=+**%@@@@@@@*        
           :%@@@@@@@%++=::::::::::::::::-=*%%%%%%#***%##%%%%%%%%%%%****#=----------=+++%@@@@@@@%:        
            =@@@@@@@@%=+-:::::::::::::::=%%****%#*%#%%#**++*%####**%%%#**+---------+++#@@@@@@@@+         
             *@@@@@@@@#=+=:::::::::::::=#*+*##%####*+++*#%%%%++++**%%%%*%**=-----=+++#@@@@@@@@#          
              #@@@@@@@@#++=:::::::::::-+*#*#%%##%###*#####%%######*###%##%##+---=+++#@@@@@@@@%           
               %@@@@@@@@%++=:::::::::-#%%##***#%%%#*=-=+*####*+=-=+*##%%*%%###+++++%@@@@@@@@%:           
               .%@@@@@@@@%*=+=::::::::-=*%#%%#%%%*+=-----==--------+%%##+#%%##**##*###*#@@@%-            
                 #@@@@@@@@@#===-::::::::-:-+=+++=--:::--------------++#++####*+#***####**#%.             
                  *@@@@@@@@@%*=+=-:::::::::::::::::::::::----=-----##**++**+++-*#######%@#               
                   +%@@@@@@@@%%*=++=::::::::::::::::::::::::-----------=++++*%#**##@@@@%+                
                    :#@@@@@%+-=*%*+=+=--::::::::::::::::::::::::----==++++*%@@@%**%@@@%-                 
                      +%@@%=-====%%#*+=++=--:::::::::::::::::::-==+++++*#%@@@@@@@@@@%+                   
                        *%#-=*-=%@@%*%%*++==++====-------====+++++++*#%@@@@@@@@@@@%*                     
                          *%*==%@@%==%@%#%%#*++==+++++++==+++++*#%%@@@@@@@@@@@@@%*                       
                            +%%@@%=-%@@%-+@#*%@%%%########%%%@@@@@@@@@@@@@@@@@%*                         
                              =#%%+#@@@@-=*-+%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%#=                           
                                 =*%@@@@=--#@@@@@@@@@@@@@@@@@@@@@@@@@@@@%#=                              
                                     +#%#*%@@@@@@@@@@@@@@@@@@@@@@@@@%#+.                                 
                                         =+*#%%@@@@@@@@@@@@@@@%#*+=                                      
                                                 -========-                                              
                                                     
	 ## ##     ####   ### ###           ### ##     ##     ### ##    ## ##   ### ###  ### ##
	##   ##     ##     ##  ##            ##  ##     ##     ##  ##  ##   ##   ##  ##   ##  ##
	##          ##     ##  ##            ##  ##   ## ##    ##  ##  ####      ##       ##  ##
	##  ###     ##     ##  ##            ##  ##   ##  ##   ## ##    #####    ## ##    ## ##
	##   ##     ##     ### ##            ## ##    ## ###   ## ##       ###   ##       ## ##
	##   ##     ##      ###              ##       ##  ##   ##  ##  ##   ##   ##  ##   ##  ##
	 ## ##     ####      ##             ####     ###  ##  #### ##   ## ##   ### ###  #### ##

""")

print("\033[0m")  # Reset color

# ============================
# Validaciones de entrada
# ============================

def pedir_ruta_pdf():
    while True:
        ruta = input("🔹 Introduce la ruta del archivo PDF: ").strip()
        if not ruta:
            print("⚠️ No puede estar vacío.")
        elif not os.path.isfile(ruta):
            print("❌ El archivo no existe.")
        elif not ruta.lower().endswith(".pdf"):
            print("🚫 El archivo no es un PDF.")
        else:
            return ruta

def pedir_directorio_pdf():
    while True:
        ruta = input("📁 Introduce la ruta del directorio con PDFs: ").strip()
        if not ruta:
            print("⚠️ No puede estar vacío.")
        elif not os.path.isdir(ruta):
            print("❌ El directorio no existe.")
        elif not any(f.lower().endswith(".pdf") for f in os.listdir(ruta)):
            print("📭 No se encontraron archivos PDF en el directorio.")
        else:
            return ruta

def pedir_nombre_salida():
    while True:
        nombre = input("💾 Introduce el nombre del archivo de salida (.txt): ").strip()
        if not nombre:
            print("⚠️ No puede estar vacío.")
        else:
            return nombre if nombre.endswith(".txt") else nombre + ".txt"

def elegir_tipo_analisis():
    print("\n📊 Tipo de análisis:")
    print("1️⃣ Análisis rápido (solo coincidencias)")
    print("2️⃣ Análisis detallado (con página/documento)")
    print("3️⃣ Análisis estructurado (bloques de página)")
    while True:
        opcion = input("Selecciona opción [1/2/3]: ").strip()
        if opcion in ["1", "2", "3"]:
            return opcion
        else:
            print("❌ Opción inválida. Introduce 1, 2 o 3.")

def confirmar_si_no(pregunta):
    while True:
        resp = input(pregunta + " (SI/NO): ").strip().lower()
        if resp in ["si", "sí", "s"]:
            return True
        elif resp in ["no", "n"]:
            return False
        else:
            print("❌ Respuesta no válida. Escribe 'SI' o 'NO'.")

def obtener_configuracion():
    salida = pedir_nombre_salida()
    modo = elegir_tipo_analisis()
    eliminar_dups = confirmar_si_no("❓ ¿Eliminar duplicados?")
    return salida, modo, eliminar_dups

# ============================
# Lógica de extracción
# ============================

def extraer_coincidencias_en_pdf(pdf_path, cadena_busqueda, modo):
    resultados = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text()
                if not texto:
                    continue
                patron = rf'\S*{re.escape(cadena_busqueda)}\S*'
                matches = re.findall(patron, texto, re.IGNORECASE)
                if modo == "1":  # Rápido
                    resultados.extend(matches)
                elif modo == "2":  # Detallado
                    for match in matches:
                        resultados.append((match, i + 1))  # texto + página
                elif modo == "3":  # Estructurado
                    if matches:
                        resultados.append((i + 1, texto))  # página + bloque de texto
    except Exception as e:
        print(f"[!] Error al procesar {pdf_path}: {e}")
    return resultados

def eliminar_duplicados(lista, modo):
    if modo == "1":
        return list(dict.fromkeys(lista))
    elif modo == "2":
        vistos = set()
        return [x for x in lista if (x[0], x[1]) not in vistos and not vistos.add((x[0], x[1]))]
    elif modo == "3":
        vistos = set()
        return [x for x in lista if (x[1]) not in vistos and not vistos.add(x[1])]

# ============================
# Procesamiento
# ============================

def procesar_archivo_individual():
    ruta = pedir_ruta_pdf()
    cadena = input("🔍 Introduce la cadena de texto a buscar: ").strip()
    salida, modo, eliminar_dups = obtener_configuracion()
    print("⏳ Procesando...")

    resultados = extraer_coincidencias_en_pdf(ruta, cadena, modo)
    if eliminar_dups:
        resultados = eliminar_duplicados(resultados, modo)

    with open(salida, "w", encoding="utf-8") as f:
        for item in resultados:
            if modo == "1":
                f.write(item + "\n")
            elif modo == "2":
                f.write(f"{item[0]} (Página {item[1]})\n")
            elif modo == "3":
                f.write(f"\n--- Página {item[0]} ---\n{item[1]}\n")

    print(f"✅ Extracción completada. Guardado en '{salida}'.")

def procesar_directorio():
    ruta_dir = pedir_directorio_pdf()
    cadena = input("🔍 Introduce la cadena de texto a buscar: ").strip()
    salida, modo, eliminar_dups = obtener_configuracion()
    print("⏳ Procesando todos los PDFs...")

    resultados = []

    for archivo in os.listdir(ruta_dir):
        if archivo.lower().endswith(".pdf"):
            pdf_path = os.path.join(ruta_dir, archivo)
            parciales = extraer_coincidencias_en_pdf(pdf_path, cadena, modo)
            for item in parciales:
                if modo == "1":
                    resultados.append(item)
                elif modo == "2":
                    resultados.append((item[0], archivo, item[1]))  # texto, archivo, página
                elif modo == "3":
                    resultados.append((archivo, item[0], item[1]))  # archivo, página, bloque

    if eliminar_dups:
        if modo == "1":
            resultados = eliminar_duplicados(resultados, modo)
        elif modo == "2":
            vistos = set()
            resultados = [x for x in resultados if (x[0], x[1], x[2]) not in vistos and not vistos.add((x[0], x[1], x[2]))]
        elif modo == "3":
            vistos = set()
            resultados = [x for x in resultados if (x[2]) not in vistos and not vistos.add(x[2])]

    with open(salida, "w", encoding="utf-8") as f:
        for item in resultados:
            if modo == "1":
                f.write(item + "\n")
            elif modo == "2":
                f.write(f"{item[0]} (Archivo: {item[1]}, Página: {item[2]})\n")
            elif modo == "3":
                f.write(f"\n===== {item[0]} =====\n--- Página {item[1]} ---\n{item[2]}\n")

    print(f"✅ Extracción completada. Guardado en '{salida}'.")

# ============================
# Menú principal
# ============================

def menu_principal():
    while True:
        print("\n📄 GIVParser v1_beta – CLI de extracción inteligente desde PDFs")
        print("1️⃣ Analizar un archivo PDF")
        print("2️⃣ Analizar todos los PDFs en un directorio")
        print("0️⃣ Salir")
        opcion = input("Selecciona una opción: ").strip()
        if opcion == "1":
            procesar_archivo_individual()
        elif opcion == "2":
            procesar_directorio()
        elif opcion == "0":
            print("👋 Saliendo del programa.")
            break
        else:
            print("❌ Opción no válida.")

if __name__ == "__main__":
    menu_principal()
