from label_studio_sdk import Client

# ========== 1. Conexão ==========
LABEL_STUDIO_URL = 'http://localhost:8080'
API_KEY = 'fb638b4f03d06b8fc5f6899383aced677f834541'  # substitua pelo seu token real

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)

# ========== 2. Ler seu export (project-15-at-2025-07-07-22-51-a5fe5b7a.json) ==========
import json

with open('project-15-at-2025-07-07-22-51-a5fe5b7a.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# ========== 3. Obter label_config do projeto original ==========
# Opcional: se quiser garantir a mesma configuração
old_project_id = 15
old_project = ls.get_project(old_project_id)
label_config = old_project.label_config

# ========== 4. Criar novo projeto duplicado ==========
new_project = ls.start_project(
    title=old_project.title + ' Copy',
    label_config=label_config
)

print(f"✅ Novo projeto criado: {new_project.id}")

# ========== 5. Preparar tasks para importação ==========
# O SDK espera tasks como lista de dicts com 'data' e opcional 'annotations'

prepared_tasks = []

for task in tasks:
    item = {
        'data': task['data']
    }

    # Se desejar importar como preannotations:
    if 'annotations' in task and task['annotations']:
        results = []
        for ann in task['annotations']:
            results.extend(ann['result'])

        item['annotations'] = [{
            "result": results,
            "completed_by": ann['completed_by'],
            "was_cancelled": ann['was_cancelled'],
            "ground_truth": ann['ground_truth']
        } for ann in task['annotations']]

    prepared_tasks.append(item)

# ========== 6. Importar tasks + annotations ==========
import_response = new_project.import_tasks(prepared_tasks)

print(f"🎉 Importação concluída. {len(import_response)} tasks importadas para projeto {new_project.id}")
