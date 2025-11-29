import cv2
import shutil
import random
from pathlib import Path
from tqdm import tqdm

def process_and_split_dataset(
    img_source_dir, 
    lbl_source_dir, 
    output_dir, 
    split_ratio=0.8, 
    clahe_clip=2.0
):
    # Configuração de Caminhos
    input_img_path = Path(img_source_dir)
    input_lbl_path = Path(lbl_source_dir)
    output_path = Path(output_dir)
    
    # Verificação de segurança
    if not input_img_path.exists():
        print(f"ERRO: A pasta de imagens não existe: {input_img_path}")
        return
    if not input_lbl_path.exists():
        print(f"ERRO: A pasta de labels não existe: {input_lbl_path}")
        return

    # Extensões válidas
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
    
    # 1. Coletar pares (Imagem, Label)
    print(f"Buscando arquivos...")
    data_pairs = []
    
    # Lista todas as imagens
    all_images = [f for f in input_img_path.iterdir() if f.suffix.lower() in valid_extensions]
    
    for img_file in all_images:
        # Busca label correspondente na pasta vizinha
        lbl_file = input_lbl_path / f"{img_file.stem}.txt"
        
        if lbl_file.exists():
            data_pairs.append((img_file, lbl_file))
        
    if not data_pairs:
        print("ERRO: Nenhuma par (imagem + .txt) encontrado.")
        return

    # 2. Embaralhar e Dividir
    random.seed(42) 
    random.shuffle(data_pairs)
    
    split_idx = int(len(data_pairs) * split_ratio)
    train_set = data_pairs[:split_idx]
    val_set = data_pairs[split_idx:]
    
    print(f"Total encontrado: {len(data_pairs)}")
    print(f"Divisão -> Treino: {len(train_set)} | Validação: {len(val_set)}")

    # CLAHE
    clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))

    def save_set(dataset, split_name):
        save_img_dir = output_path / 'images' / split_name
        save_lbl_dir = output_path / 'labels' / split_name
        save_img_dir.mkdir(parents=True, exist_ok=True)
        save_lbl_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Processando {split_name}...")
        for img_path, lbl_path in tqdm(dataset):
            # A. Ler e Aplicar CLAHE
            img = cv2.imread(str(img_path))
            if img is None: continue
            
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_clahe = clahe.apply(l)
            lab_merged = cv2.merge((l_clahe, a, b))
            img_final = cv2.cvtColor(lab_merged, cv2.COLOR_LAB2BGR)
            
            # B. Salvar
            cv2.imwrite(str(save_img_dir / img_path.name), img_final)
            shutil.copy(lbl_path, save_lbl_dir / lbl_path.name)

    # 3. Executar
    if len(train_set) > 0: save_set(train_set, 'train')
    if len(val_set) > 0: save_set(val_set, 'val')
    
    print(f"\nSUCESSO! Novo dataset criado em: {output_path.absolute()}")

# --- CONFIGURAÇÃO (AJUSTE AQUI) ---

# Caminho da pasta principal que contém "images" e "labels"
CAMINHO_RAIZ = "datasets/todas_imagens" 

# Caminhos derivados (não precisa mexer)
ORIGEM_IMAGENS = f"{CAMINHO_RAIZ}/images"
ORIGEM_LABELS  = f"{CAMINHO_RAIZ}/labels"

# Onde será salvo o dataset final pronto para treino
DESTINO_DATASET = "datasets/dataset_yolo_clahe"

if __name__ == "__main__":
    process_and_split_dataset(
        ORIGEM_IMAGENS, 
        ORIGEM_LABELS, 
        DESTINO_DATASET, 
        split_ratio=0.8
    )