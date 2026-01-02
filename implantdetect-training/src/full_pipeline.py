import os
import glob
import shutil
import yaml
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm
from collections import Counter
from sklearn.model_selection import train_test_split
from ultralytics import YOLO

# =================================================================================================
#                                     CONFIGURAÇÕES GERAIS
# =================================================================================================

# --- Caminhos Base ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # .../implantdetect-training
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw', 'todas_imagens_rotuladas')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

# --- Configurações do CLAHE ---
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# --- Configurações de Estratificação ---
TEST_SIZE = 0.20
RANDOM_STATE = 42
EXTENSOES_IMAGEM = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']

# --- Configurações de Treino (YOLO) ---
MODEL_NAME = 'yolo8s-obb.pt'  # Modelo base
EPOCHS = 200
BATCH_SIZE = 16
IMG_SIZE = 640
DEVICE = 0

# --- Dicionário de Classes (Completo) ---
ALL_CLASSES_NAMES = {
    0: "CMSW 3813", 1: "CMSW 4510", 2: "ILCM 3510", 3: "ILCM 3511", 4: "ILCM 3513",
    5: "ILCM 3810", 6: "ILCM 3811", 7: "ILCM 3813", 8: "ILCM 3885", 9: "ILCM 4510",
    10: "ILCM 4511", 11: "ILCM 4585", 12: "ILHE 3510", 13: "ILHE 3511", 14: "ILHE 3711",
    15: "ILHE 3785", 16: "ILHE 4010", 17: "ILHE 4011", 18: "ILHE 4510", 19: "ILHE 4511",
    20: "ILHE 4585", 21: "Master AR - Torq Porous NP 3,75 x 13,0mm", 22: "Master Connect AR 3,75 x 11,5mm",
    23: "Master Connect AR 5,0 x 10,0mm", 24: "Master Easy - Grip Actives RD 3,75 x 10,0mm",
    25: "Master Easy - Grip Actives RD 3,75 x 11,5mm", 26: "Master Easy - Grip Porous RD 3,75 x 10,0mm",
    27: "Master Easy - Grip Porous RD 3,75 x 11,5mm", 28: "Master Easy - Grip Porous RD 3,75 x 13,0mm",
    29: "Master Easy - Grip Porous RD 3,75 x 8,5mm", 30: "Master Easy - Grip Porous RD 4,0 x 10,0mm",
    31: "SA 313", 32: "SA 411", 33: "SCO 3510", 34: "SCW 3211", 35: "SCW 3707",
    36: "SCW 3710", 37: "SCW 3711", 38: "SCW 3713", 39: "SCW 3785", 40: "SW 3811",
    41: "SW 3885", 42: "SW 4513", 43: "SW 5085", 44: "SWCM 3513", 45: "SWCM 3585",
    46: "SWCM 4513", 47: "SWCM 5010", 48: "SWHE 3710", 49: "Titamax Ti Cortical (4,1) 3,75 x 11,0mm",
    50: "Titamax Ti Ex (4,1) 3,75 x 13,0mm", 51: "UCM 3510", 52: "UCM 3511", 53: "UCM 4310"
}

# CLASSES_TO_REMOVE = set([53, 51, 47, 18, 17, 11, 7, 12, 46, 22, 21, 23, 45, 20, 13, 1, 30, 52, 41, 8, 44, 16, 9, 27, 33, 43, 40, 3, 24, 48, 14, 2, 10, 34, 42])
CLASSES_ALVO = set([5, 29, 36, 37, 38, 39, 49, 50])


# =================================================================================================
#                                     UTILITÁRIOS
# =================================================================================================

def count_classes_in_directory(directory, stage_name):
    """ Conta e exibe estatísticas das classes presentes no diretório fornecido. """
    print(f"\n=== ESTATÍSTICAS: {stage_name} ===")
    print(f"Analisando diretório: {directory}")
    
    # Busca recursiva por arquivos .txt
    label_files = glob.glob(os.path.join(directory, '**', '*.txt'), recursive=True)
    
    if not label_files:
        print(" -> Nenhum arquivo de label encontrado.")
        return

    class_counts = Counter()
    total_objects = 0
    
    for file_path in label_files:
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    try:
                        class_id = int(parts[0])
                        class_counts[class_id] += 1
                        total_objects += 1
                    except ValueError:
                        pass
    
    print(f" -> Total de Arquivos de Label: {len(label_files)}")
    print(f" -> Total de Objetos: {total_objects}")
    print(f" -> Classes Únicas: {len(class_counts)}")
    
    print("\n[Detalhamento por Classe]")
    for class_id in sorted(class_counts.keys()):
        name = ALL_CLASSES_NAMES.get(class_id, f"Unknown ID {class_id}")
        print(f"   ID {class_id:2d}: {class_counts[class_id]:4d} ocorrências | {name}")
    print("=================================================\n")


# =================================================================================================
#                                     PASSO 1: APLICAÇÃO DO CLAHE
# =================================================================================================

def apply_clahe_to_image(image):
    """ Aplica CLAHE e retorna a imagem em escala de cinza (preto e branco). """
    if image is None: return None

    # Se for colorida (3 canais), converte para escala de cinza
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplica CLAHE na imagem em escala de cinza
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID_SIZE)
    return clahe.apply(image)

def step_1_clahe(output_dir):
    """
    Lê imagens de RAW_DATA_DIR, aplica CLAHE e salva em output_dir.
    Copia os labels sem modificação.
    """
    print(f"\n=== PASSO 1: CLAHE ===")
    print(f"Origem: {RAW_DATA_DIR}")
    print(f"Destino: {output_dir}")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    src_img_dir = os.path.join(RAW_DATA_DIR, 'images')
    src_lbl_dir = os.path.join(RAW_DATA_DIR, 'labels')
    
    dest_img_dir = os.path.join(output_dir, 'images')
    dest_lbl_dir = os.path.join(output_dir, 'labels')
    
    os.makedirs(dest_img_dir, exist_ok=True)
    os.makedirs(dest_lbl_dir, exist_ok=True)

    # Listar imagens
    image_files = set()
    for ext in EXTENSOES_IMAGEM:
        image_files.update(glob.glob(os.path.join(src_img_dir, f"*{ext}")))
        image_files.update(glob.glob(os.path.join(src_img_dir, f"*{ext.upper()}")))
    
    image_files = list(image_files)

    print(f"Processando {len(image_files)} imagens...")

    for img_path in tqdm(image_files, desc="Aplicando CLAHE"):
        filename = os.path.basename(img_path)
        
        # Processar Imagem
        img = cv2.imread(img_path)
        if img is None:
            print(f"Erro ao ler: {img_path}")
            continue
            
        img_clahe = apply_clahe_to_image(img)
        cv2.imwrite(os.path.join(dest_img_dir, filename), img_clahe)
        
        # Copiar Label
        label_name = os.path.splitext(filename)[0] + '.txt'
        src_label_path = os.path.join(src_lbl_dir, label_name)
        if os.path.exists(src_label_path):
            shutil.copy(src_label_path, os.path.join(dest_lbl_dir, label_name))

    return output_dir


# =================================================================================================
#                                     PASSO 2: ESTRATIFICAÇÃO
# =================================================================================================

def load_labels_info(labels_path):
    """ Lê os arquivos .txt e identifica a classe para estratificação. """
    data = []
    label_files = glob.glob(os.path.join(labels_path, "*.txt"))
    
    for file_path in label_files:
        filename = os.path.basename(file_path).replace('.txt', '')
        classes = []
        if os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        classes.append(int(parts[0]))
        
        primary_class = Counter(classes).most_common(1)[0][0] if classes else -1
        data.append({'filename': filename, 'stratify_target': primary_class, 'label_path': file_path})

    return pd.DataFrame(data)

def copy_stratified_files(df, subset_name, src_img_dir, dest_base_dir):
    img_dest = os.path.join(dest_base_dir, 'images', subset_name)
    lbl_dest = os.path.join(dest_base_dir, 'labels', subset_name)
    os.makedirs(img_dest, exist_ok=True)
    os.makedirs(lbl_dest, exist_ok=True)

    for _, row in df.iterrows():
        # Copiar Label
        shutil.copy(row['label_path'], os.path.join(lbl_dest, os.path.basename(row['label_path'])))
        
        # Copiar Imagem (procurar extensão correta)
        found = False
        for ext in EXTENSOES_IMAGEM:
            for candidate in [row['filename'] + ext, row['filename'] + ext.upper()]:
                src_path = os.path.join(src_img_dir, candidate)
                if os.path.exists(src_path):
                    shutil.copy(src_path, os.path.join(img_dest, candidate))
                    found = True
                    break
            if found: break

def step_2_stratification(input_dir, output_dir):
    """
    Lê do diretório com CLAHE, divide em Train/Val e salva em output_dir.
    """
    print(f"\n=== PASSO 2: ESTRATIFICAÇÃO ===")
    print(f"Origem: {input_dir}")
    print(f"Destino: {output_dir}")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    src_labels = os.path.join(input_dir, 'labels')
    src_images = os.path.join(input_dir, 'images')

    df = load_labels_info(src_labels)
    if df.empty:
        print("Nenhum label encontrado!")
        return None

    # Separar classes raras (< 2 amostras)
    counts = df['stratify_target'].value_counts()
    rare_classes = counts[counts < 2].index.tolist()
    
    df_rare = df[df['stratify_target'].isin(rare_classes)]
    df_common = df[~df['stratify_target'].isin(rare_classes)]

    if rare_classes:
        print(f"Classes raras (forçadas para treino): {rare_classes}")

    # Divisão
    train_common, val_common = train_test_split(
        df_common, test_size=TEST_SIZE, stratify=df_common['stratify_target'], random_state=RANDOM_STATE
    )

    train_df = pd.concat([train_common, df_rare]) if not df_rare.empty else train_common
    val_df = val_common

    print(f"Treino: {len(train_df)} | Validação: {len(val_df)}")

    # Copiar
    copy_stratified_files(train_df, 'train', src_images, output_dir)
    copy_stratified_files(val_df, 'val', src_images, output_dir)

    return output_dir


# =================================================================================================
#                                     PASSO 3: FILTRAGEM E TREINO
# =================================================================================================

def filter_and_prepare_final_dataset(source_dir, dest_dir, classes_to_keep):
    """
    Copia o dataset estratificado para uma pasta final, filtrando classes indesejadas.
    Renomeia os IDs das classes para serem sequenciais (0..N).
    """
    print(f"\n=== PASSO 3: PREPARAÇÃO FINAL E TREINO ===")
    print(f"Filtrando dataset para {len(classes_to_keep)} classes...")
    
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    shutil.copytree(source_dir, dest_dir)

    # Mapeamento: ID Original -> Novo ID Sequencial
    id_mapping = {old_id: new_id for new_id, old_id in enumerate(classes_to_keep)}
    
    total_removed = 0
    
    for split in ['train', 'val']:
        labels_path = os.path.join(dest_dir, 'labels', split)
        images_path = os.path.join(dest_dir, 'images', split)
        
        if not os.path.exists(labels_path): continue

        for txt_file in glob.glob(os.path.join(labels_path, "*.txt")):
            with open(txt_file, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                parts = line.strip().split()
                if not parts: continue
                cls_id = int(parts[0])
                
                if cls_id in classes_to_keep:
                    parts[0] = str(id_mapping[cls_id])
                    new_lines.append(" ".join(parts) + "\n")
            
            if new_lines:
                with open(txt_file, 'w') as f:
                    f.writelines(new_lines)
            else:
                # Remove arquivo se ficou vazio (imagem sem labels úteis)
                os.remove(txt_file)
                basename = os.path.splitext(os.path.basename(txt_file))[0]
                for img in glob.glob(os.path.join(images_path, f"{basename}.*")):
                    os.remove(img)
                total_removed += 1
                
    print(f"Imagens removidas (sem classes alvo): {total_removed}")
    return dest_dir

def create_yaml_config(dataset_path, classes_to_keep, run_name):
    new_names = {i: ALL_CLASSES_NAMES[old_id] for i, old_id in enumerate(classes_to_keep)}
    
    yaml_content = {
        'path': dataset_path,
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(classes_to_keep),
        'names': new_names
    }
    
    config_dir = os.path.join(BASE_DIR, 'config')
    os.makedirs(config_dir, exist_ok=True)
    yaml_path = os.path.join(config_dir, f"{run_name}.yaml")
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, sort_keys=False)
    
    return yaml_path

def step_3_train(input_dir, run_name):
    # 1. Preparar Dataset Final (Filtrado)
    final_dataset_dir = os.path.join(PROCESSED_DIR, f"dataset_{run_name}")
    filter_and_prepare_final_dataset(input_dir, final_dataset_dir, CLASSES_ALVO)
    
    # 2. Criar YAML
    yaml_path = create_yaml_config(final_dataset_dir, CLASSES_ALVO, run_name)
    print(f"YAML criado em: {yaml_path}")
    
    # 3. Carregar Modelo
    models_dir = os.path.join(BASE_DIR, 'models', 'pretrained')
    model_path = os.path.join(models_dir, MODEL_NAME)
    if not os.path.exists(model_path):
        print(f"Modelo local não encontrado em {model_path}, baixando/usando padrão '{MODEL_NAME}'...")
        model_path = MODEL_NAME
        
    model = YOLO(model_path)
    
    # 4. Treinar
    print(f"Iniciando treinamento: {run_name}")
    results = model.train(
        data=yaml_path,
        project=os.path.join(BASE_DIR, 'models', 'runs'),
        name=run_name,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH_SIZE,
        device=DEVICE,
        degrees=15.0,
        fliplr=0.5,
        flipud=0.5,
        hsv_h=0.0, hsv_s=0.0, hsv_v=0.0,
        mosaic=1.0
    )
    print(f"Treino finalizado! Resultados em models/runs/{run_name}")


# =================================================================================================
#                                     EXECUÇÃO PRINCIPAL
# =================================================================================================

def main():
    base_run_prefix = "pipeline_completo_clahe"

    # 1. CLAHE (executar uma vez)
    dir_clahe = os.path.join(PROCESSED_DIR, f"{base_run_prefix}_temp_step1_clahe")
    step_1_clahe(dir_clahe)
    count_classes_in_directory(dir_clahe, "PÓS-CLAHE (Dataset Completo)")

    # 2. Estratificação (executar uma vez)
    dir_stratified = os.path.join(PROCESSED_DIR, f"{base_run_prefix}_temp_step2_stratified")
    step_2_stratification(dir_clahe, dir_stratified)
    count_classes_in_directory(os.path.join(dir_stratified, 'labels', 'train'), "ESTRATIFICAÇÃO - TREINO")
    count_classes_in_directory(os.path.join(dir_stratified, 'labels', 'val'), "ESTRATIFICAÇÃO - VALIDAÇÃO")

    # 3. Treinos em loop: yolov8 e yolov11 nas variantes nano, small e medium
    versions = ['8', '11']                  # v8 and v11
    sizes = {'n': 'nano', 's': 'small', 'm': 'medium'}
    epochs_list = [50, 100, 200]

    for ver in versions:
        for size_code, size_name in sizes.items():
            for epoch in epochs_list:
                # Ajusta o nome do modelo global para que step_3_train use o correto.
                # Ex.: 'yolov8n-obb.pt', 'yolo11n-obb.pt'
                if ver == '8':
                    model_name = f"yolov{ver}{size_code}-obb.pt"
                else:
                    model_name = f"yolo{ver}{size_code}-obb.pt"

                global MODEL_NAME
                MODEL_NAME = model_name
                
                global EPOCHS
                EPOCHS = epoch

                run_name = f"{base_run_prefix}_v{ver}_{size_name}_{epoch}e"
                print(f"\n=== INICIANDO: {run_name} | Modelo: {MODEL_NAME} | Épocas: {EPOCHS} ===")
                step_3_train(dir_stratified, run_name)

if __name__ == "__main__":
    main()
