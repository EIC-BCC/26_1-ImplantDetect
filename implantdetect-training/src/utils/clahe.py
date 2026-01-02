import cv2
import os
import glob
import shutil
import numpy as np
from tqdm import tqdm

# ================= CONFIGURAÇÕES =================
# Nome da pasta de entrada (resultado do script de estratificação)
INPUT_DATASET = 'dataset_rotulado_stratified' 

# Nome da pasta de saída (onde ficarão as imagens com CLAHE)
OUTPUT_DATASET = 'dataset_rotulado_stratified_clahe'

# Parâmetros do CLAHE
CLIP_LIMIT = 2.0
TILE_GRID_SIZE = (8, 8)

# Caminhos Base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(BASE_DIR, 'data', 'processed', INPUT_DATASET)
DEST_DIR = os.path.join(BASE_DIR, 'data', 'processed', OUTPUT_DATASET)

def apply_clahe(image):
    """
    Aplica CLAHE em imagens coloridas (LAB) ou em tons de cinza.
    """
    # Se a imagem for carregada como None (erro de leitura)
    if image is None:
        return None

    # Verifica se é escala de cinza ou colorida
    if len(image.shape) == 2:  # Grayscale
        clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=TILE_GRID_SIZE)
        return clahe.apply(image)
    
    else:  # Colorida (BGR)
        # Converter para LAB (Luminosidade, A, B)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Aplicar CLAHE apenas no canal L (Luminosidade)
        clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=TILE_GRID_SIZE)
        l2 = clahe.apply(l)
        
        # Mesclar canais e converter de volta para BGR
        lab = cv2.merge((l2, a, b))
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

def process_subset(subset_name):
    """
    Processa um subconjunto (train ou val):
    1. Aplica CLAHE nas imagens.
    2. Copia os labels correspondentes.
    """
    src_img_path = os.path.join(SRC_DIR, 'images', subset_name)
    src_lbl_path = os.path.join(SRC_DIR, 'labels', subset_name)
    
    dest_img_path = os.path.join(DEST_DIR, 'images', subset_name)
    dest_lbl_path = os.path.join(DEST_DIR, 'labels', subset_name)
    
    # Criar diretórios de destino
    os.makedirs(dest_img_path, exist_ok=True)
    os.makedirs(dest_lbl_path, exist_ok=True)
    
    # Listar imagens
    # Suporta várias extensões
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tif', '*.tiff']
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(src_img_path, ext)))
        # Tenta versão maiúscula também
        image_files.extend(glob.glob(os.path.join(src_img_path, ext.upper())))
    
    print(f"Processando '{subset_name}': {len(image_files)} imagens encontradas.")
    
    for img_path in tqdm(image_files, desc=f"CLAHE {subset_name}"):
        filename = os.path.basename(img_path)
        
        # 1. Processar Imagem
        img = cv2.imread(img_path)
        img_clahe = apply_clahe(img)
        
        if img_clahe is not None:
            save_path = os.path.join(dest_img_path, filename)
            cv2.imwrite(save_path, img_clahe)
            
            # 2. Copiar Label Correspondente
            # Assume que o label tem o mesmo nome base da imagem, mas extensão .txt
            label_name = os.path.splitext(filename)[0] + '.txt'
            src_label_file = os.path.join(src_lbl_path, label_name)
            
            if os.path.exists(src_label_file):
                shutil.copy(src_label_file, os.path.join(dest_lbl_path, label_name))
            else:
                # Se não tem label (ex: imagem de background), apenas ignora a cópia do label
                pass
        else:
            print(f"Erro ao ler imagem: {img_path}")

def main():
    print("--- Iniciando Aplicação de CLAHE ---")
    print(f"Origem: {SRC_DIR}")
    print(f"Destino: {DEST_DIR}")
    
    if not os.path.exists(SRC_DIR):
        print(f"ERRO: Diretório de origem não encontrado: {SRC_DIR}")
        print("Execute o script de divisão estratificada primeiro.")
        return

    # Limpar destino se existir para evitar mistura de dados antigos
    if os.path.exists(DEST_DIR):
        print("Removendo pasta de destino antiga...")
        shutil.rmtree(DEST_DIR)

    # Processar Treino
    process_subset('train')
    
    # Processar Validação
    process_subset('val')
    
    print("\n--- Processo Concluído ---")
    print(f"Novo dataset gerado em: {DEST_DIR}")

if __name__ == "__main__":
    main()