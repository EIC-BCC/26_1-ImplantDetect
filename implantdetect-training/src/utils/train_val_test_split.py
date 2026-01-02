import os
import shutil
import glob
import pandas as pd
from sklearn.model_selection import train_test_split
from collections import Counter
from tqdm import tqdm

# ================= CONFIGURAÇÕES =================
NOME_DATASET_SAIDA = 'dataset_rotulado_stratified_final'
EXTENSOES_IMAGEM = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']

# Caminhos Base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw', 'todas_imagens_rotuladas')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed', NOME_DATASET_SAIDA)

def load_labels_info(labels_path):
    """ Lê os arquivos .txt e identifica a classe para estratificação. """
    data = []
    label_files = glob.glob(os.path.join(labels_path, "*.txt"))
    
    print(f"[1/5] Lendo {len(label_files)} arquivos de labels em: {labels_path}")

    for file_path in tqdm(label_files):
        filename = os.path.basename(file_path).replace('.txt', '')
        classes = []
        
        if os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split()
                    if parts:
                        classes.append(int(parts[0]))
        
        if not classes:
            primary_class = -1 
        else:
            primary_class = Counter(classes).most_common(1)[0][0]

        data.append({
            'filename': filename,
            'stratify_target': primary_class,
            'label_path': file_path
        })

    return pd.DataFrame(data)

def copy_files(df, subset_name, src_img_dir, dest_base_dir):
    """ Copia as imagens e labels para as pastas de destino. """
    img_dest = os.path.join(dest_base_dir, 'images', subset_name)
    lbl_dest = os.path.join(dest_base_dir, 'labels', subset_name)
    
    os.makedirs(img_dest, exist_ok=True)
    os.makedirs(lbl_dest, exist_ok=True)

    print(f" -> Copiando {len(df)} arquivos para '{subset_name}'...")

    missing_images = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        shutil.copy(row['label_path'], os.path.join(lbl_dest, os.path.basename(row['label_path'])))
        
        found_img = False
        for ext in EXTENSOES_IMAGEM:
            candidates = [row['filename'] + ext, row['filename'] + ext.upper()]
            for img_name in candidates:
                src_img_path = os.path.join(src_img_dir, img_name)
                if os.path.exists(src_img_path):
                    shutil.copy(src_img_path, os.path.join(img_dest, img_name))
                    found_img = True
                    break
            if found_img: break
        
        if not found_img:
            missing_images.append(row['filename'])

    if missing_images:
        print(f"ATENÇÃO: {len(missing_images)} imagens não foram encontradas.")

def main():
    print(f"--- Iniciando Estratificação ---")
    
    src_labels = os.path.join(RAW_DATA_DIR, 'labels')
    src_images = os.path.join(RAW_DATA_DIR, 'images')

    # 1. Carregar metadados
    df = load_labels_info(src_labels)
    if df.empty: return

    # 2. Analisar Distribuição e Separar Classes Raras
    counts = df['stratify_target'].value_counts()
    print("\n[2/5] Distribuição de Classes:")
    print(counts.sort_index())

    # Identificar classes com menos de 2 amostras
    rare_classes = counts[counts < 2].index.tolist()
    
    if rare_classes:
        print(f"\nAVISO: As classes {rare_classes} têm apenas 1 amostra. Elas serão forçadas para o TREINO.")
        
        # Separa o dataframe em dois
        df_rare = df[df['stratify_target'].isin(rare_classes)]
        df_common = df[~df['stratify_target'].isin(rare_classes)]
    else:
        df_rare = pd.DataFrame()
        df_common = df

    # 3. Divisão Estratificada (Apenas nas classes comuns)
    train_common, val_common = train_test_split(
        df_common, 
        test_size=0.20, 
        stratify=df_common['stratify_target'], 
        random_state=42
    )

    # 4. Juntar as classes raras no Treino
    if not df_rare.empty:
        train_df = pd.concat([train_common, df_rare])
    else:
        train_df = train_common
        
    val_df = val_common

    print(f"\n[3/5] Divisão Final realizada:")
    print(f" - Treino: {len(train_df)} imagens (incluindo {len(df_rare)} raras)")
    print(f" - Validação: {len(val_df)} imagens")

    # 5. Limpeza e Cópia
    if os.path.exists(PROCESSED_DIR):
        shutil.rmtree(PROCESSED_DIR)
    
    print(f"\n[4/5] Copiando arquivos...")
    copy_files(train_df, 'train', src_images, PROCESSED_DIR)
    copy_files(val_df, 'val', src_images, PROCESSED_DIR)

    print(f"\n--- Processo Concluído ---")
    print(f"Local: {PROCESSED_DIR}")

if __name__ == "__main__":
    main()