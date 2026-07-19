import os
import pandas as pd

def cargar_datos_xls():
    xls_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/spreadsheets/'))
    if not os.path.exists(xls_dir) or not os.listdir(xls_dir):
        raise FileNotFoundError(f"No se encontró la carpeta de datos: {xls_dir}")
    
    archivos = [f for f in os.listdir(xls_dir) if f.endswith('.xlsx')]
    if not archivos:
        raise FileNotFoundError(f"No se encontró ningún archivo Excel (.xlsx) en {xls_dir}")
    
    xls_path = os.path.join(xls_dir, archivos[0])
    df = pd.read_excel(xls_path)
    
    return df