import os
import shutil
import glob
import yaml
from ultralytics import YOLO

# --- DICIONÁRIO COMPLETO DE CLASSES (Para gerar o YAML correto) ---
ALL_CLASSES_NAMES = {
    0: "CMSW 3813", 1: "CMSW 4510", 2: "ILCM 3510", 3: "ILCM 3511", 4: "ILCM 3513",
    5: "ILCM 3810", 6: "ILCM 3811", 7: "ILCM 3813", 8: "ILCM 3885", 9: "ILCM 4510",
    10: "ILCM 4511", 11: "ILCM 4585", 12: "ILHE 3510", 13: "ILHE 3511", 14: "ILHE 3711",
    15: "ILHE 3785", 16: "ILHE 4010", 17: "ILHE 4011", 18: "ILHE 4510", 19: "ILHE 4511",
    20: "ILHE 4585", 21: "Master AR - Torq Porous NP 3,75 x 13,0mm", 22: "Master Connect AR 3,75 x 11,5mm",
    23: "Master Connect AR 5,0 x 10,0mm", 24: "Master Easy - Grip Actives RD 3,75 x 10,0mm",
    25: "Master Easy - Grip Actives RD 3,75 x 11,5mm", 26: "Master Easy - Grip Porous RD 3,75 x 10,0mm",
    27: "Master Easy - Grip Porous RD 3,75 x 11,5mm", 28: "Master Easy - Grip Porous RD 3,75 x 13,0mm",
    29: "Master Easy - Grip Porous RD 3,75 x 8,5mm", 30: "SA 313", 31: "SA 411", 32: "SCO 3510",
    33: "SCW 3211", 34: "SCW 3707", 35: "SCW 3710", 36: "SCW 3711", 37: "SCW 3713",
    38: "SCW 3785", 39: "SW 3811", 40: "SW 3885", 41: "SW 4513", 42: "SW 5085",
    43: "SWCM 3513", 44: "SWCM 4513", 45: "SWCM 5010", 46: "SWHE 3710",
    47: "Titamax Ti Cortical (4,1) 3,75 x 11,0mm", 48: "Titamax Ti Ex (4,1) 3,75 x 13,0mm"
}

def setup_paths():
    """Configura caminhos dinâmicos baseados na localização deste script."""
    base_dir = os.path.dirname(os.path.abspath(__file__)) # .../src
    root_dir = os.path.dirname(base_dir)                  # .../implantdetect-training
    
    paths = {
        'root': root_dir,
        'config': os.path.join(root_dir, 'config'),
        'data_processed': os.path.join(root_dir, 'data', 'processed'),
        'models_pretrained': os.path.join(root_dir, 'models', 'pretrained'),
        'runs_output': os.path.join(root_dir, 'models', 'runs'),
        # Define qual dataset original será usado como base para as cópias
        'original_dataset': os.path.join(root_dir, 'data', 'processed', 'dataset_yolo_clahe2') 
    }
    return paths

def filter_dataset(source, destination, classes_to_keep):
    """Copia o dataset, filtra as classes e remove imagens vazias."""
    print(f"   -> Copiando dados de:\n      {source}\n      para:\n      {destination}")
    
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)

    # Mapa: ID Antigo -> ID Novo (0, 1, 2...)
    id_mapping = {old_id: new_id for new_id, old_id in enumerate(classes_to_keep)}
    
    total_imgs_removed = 0

    # Itera sobre train e val
    for split in ['train', 'val']:
        labels_path = os.path.join(destination, 'labels', split)
        images_path = os.path.join(destination, 'images', split)
        
        if not os.path.exists(labels_path): continue

        txt_files = glob.glob(os.path.join(labels_path, "*.txt"))
        
        for txt_file in txt_files:
            with open(txt_file, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                parts = line.strip().split()
                if not parts: continue
                
                # OBB ou YOLO Normal: o ID da classe é sempre o primeiro elemento
                cls_id = int(parts[0])
                
                if cls_id in classes_to_keep:
                    # Atualiza o ID da classe para o novo índice sequencial
                    parts[0] = str(id_mapping[cls_id])
                    new_lines.append(" ".join(parts) + "\n")
            
            # SE AINDA EXISTIREM ANOTAÇÕES, SALVA.
            if new_lines:
                with open(txt_file, 'w') as f:
                    f.writelines(new_lines)
            
            # SE FICOU VAZIO, DELETA TUDO.
            else:
                os.remove(txt_file) # Remove .txt
                
                # Remove imagem correspondente
                basename = os.path.splitext(os.path.basename(txt_file))[0]
                # Busca extensões comuns
                img_candidates = glob.glob(os.path.join(images_path, f"{basename}.*"))
                for img in img_candidates:
                    os.remove(img)
                total_imgs_removed += 1
                
    print(f"   -> Filtragem concluída. Imagens removidas (vazias): {total_imgs_removed}")

def create_run_yaml(paths, run_code, dataset_dest_path, classes_to_keep):
    """Gera o arquivo YAML específico para a execução."""
    new_names = {i: ALL_CLASSES_NAMES[old_id] for i, old_id in enumerate(classes_to_keep)}
    
    yaml_content = {
        'path': dataset_dest_path,
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test', # Opcional, se existir
        'nc': len(classes_to_keep),
        'names': new_names
    }
    
    yaml_filename = f"data_{run_code}.yaml"
    yaml_path = os.path.join(paths['config'], yaml_filename)
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, sort_keys=False)
        
    return yaml_path

def run_pipeline(run_code, classes_to_keep, model_name='yolo11m-obb.pt', epochs=100):
    paths = setup_paths()
    print(f"=== INICIANDO PIPELINE: {run_code} ===")
    
    # 1. Preparar Dataset Específico (Filtro Físico)
    dataset_run_folder = f"dataset_{run_code}"
    dataset_dest_path = os.path.join(paths['data_processed'], dataset_run_folder)
    
    filter_dataset(paths['original_dataset'], dataset_dest_path, classes_to_keep)
    
    # 2. Criar YAML Específico
    yaml_path = create_run_yaml(paths, run_code, dataset_dest_path, classes_to_keep)
    print(f"   -> YAML criado: {yaml_path}")
    
    # 3. Configurar Modelo
    model_local_path = os.path.join(paths['models_pretrained'], model_name)
    model_to_use = model_local_path if os.path.exists(model_local_path) else model_name
    
    print(f"   -> Carregando modelo: {model_to_use}")
    model = YOLO(model_to_use)

    # 4. Iniciar Treino (Seus parâmetros originais mantidos aqui)
    print(f"   -> Iniciando treinamento...")
    results = model.train(
        data=yaml_path,
        project=paths['runs_output'],
        name=run_code,
        
        # Parâmetros Gerais
        epochs=epochs,
        imgsz=640,
        batch=16,
        device=0,
        
        # --- AUGMENTATIONS (Mantidos do seu script) ---
        degrees=15.0,
        fliplr=0.5,
        flipud=0.5,
        
        # --- COR (Mantido desativado como solicitado) ---
        hsv_h=0.0,
        hsv_s=0.0,
        hsv_v=0.0,
        
        # --- OUTROS ---
        mosaic=1.0,
        
        # OBS: Removemos 'classes=[...]' daqui, pois já filtramos o dataset fisicamente!
    )
    
    print(f"=== SUCESSO! Resultados em: {os.path.join(paths['runs_output'], run_code)} ===")

if __name__ == '__main__':
    # --- CONFIGURAÇÃO DA EXECUÇÃO ---
    
    # 1. Defina um nome para este experimento (será o nome da pasta em runs/)
    CODIGO_EXECUCAO = "teste1"
    
    # 2. Defina os IDs das classes ORIGINAIS que deseja MANTER
    # Se uma imagem não tiver nenhuma dessas classes, ela será ignorada no treino.
    CLASSES_ALVO = {29, 36, 37, 38, 47}
    
    # 3. Configurações do modelo
    NOME_MODELO = 'yolo11m-obb.pt' # Pode ser 'yolo11n.pt', 'yolo11n-obb.pt', etc.
    EPOCAS = 50

    run_pipeline(CODIGO_EXECUCAO, CLASSES_ALVO, NOME_MODELO, EPOCAS)