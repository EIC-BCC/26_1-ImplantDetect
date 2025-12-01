import os
from ultralytics import YOLO

def train_yolo_obb():
    # --- CONFIGURAÇÃO DE CAMINHOS DINÂMICOS ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)
    
    # Caminhos para os arquivos
    YAML_PATH = os.path.join(ROOT_DIR, 'config', 'data_clahe_1.yaml')
    MODEL_LOCAL_PATH = os.path.join(ROOT_DIR, 'models', 'pretrained', 'yolo11m-obb.pt')
    MODEL_TO_USE = MODEL_LOCAL_PATH if os.path.exists(MODEL_LOCAL_PATH) else 'yolo11m-obb.pt'
    
    # Onde salvar os resultados (runs): .../implantdetect-training/models/runs
    OUTPUT_DIR = os.path.join(ROOT_DIR, 'models', 'runs')

    print(f"--> Configuração do Treino:")
    print(f"    YAML: {YAML_PATH}")
    print(f"    Modelo: {MODEL_TO_USE}")
    print(f"    Saída: {OUTPUT_DIR}")

    # 1. Carregar o modelo
    model = YOLO(MODEL_TO_USE) 

    # 2. Iniciar Treinamento
    results = model.train(
        data=YAML_PATH,                 # Caminho absoluto para o yaml
        project=OUTPUT_DIR,             # Define a pasta raiz de saída
        name='yolo11_obb_clahe_run',    # Nome da subpasta do experimento
        classes = [1],
        
        epochs=100,
        imgsz=640,
        batch=16,
        device=0,
        
        # --- AUGMENTATIONS (Mantidos originais) ---
        degrees=15.0,
        fliplr=0.5,
        flipud=0.5,
        
        # --- DESATIVAR ALTERAÇÕES DE COR ---
        hsv_h=0.0,
        hsv_s=0.0,
        hsv_v=0.0,
        
        # --- OUTRAS CONFIGURAÇÕES ---
        mosaic=1.0,
    )

    print(f"Treinamento finalizado. Resultados salvos em: {os.path.join(OUTPUT_DIR, 'yolo11_obb_clahe_run')}")

if __name__ == '__main__':
    train_yolo_obb()