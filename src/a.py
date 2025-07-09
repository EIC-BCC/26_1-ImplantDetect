from label_studio_sdk import Client

# ========== 1. Conexão ==========
LABEL_STUDIO_URL = 'http://localhost:8080'
API_KEY = 'fb638b4f03d06b8fc5f6899383aced677f834541'  # substitua pelo seu token real

ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)

# ========== 2. Ler seu export (project-15-at-2025-07-07-22-51-a5fe5b7a.json) ==========
import json

with open('project-15-at-2025-07-07-22-51-a5fe5b7a.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# ========== 3. Obter configurações do projeto original ==========
old_project_id = 15
old_project = ls.get_project(old_project_id)
label_config = old_project.label_config

# Obter configurações de armazenamento do projeto original
storage_configs = old_project.get_storages()
storage_connections = []
for storage in storage_configs:
    storage_connections.append({
        'storage_type': storage['type'],
        'storage_config': storage
    })

# ========== 4. Criar novo projeto duplicado ==========
new_project = ls.start_project(
    title=old_project.title + ' Copy',
    label_config=label_config,
    description=old_project.description
)

print(f"✅ Novo projeto criado: {new_project.id}")

# ========== 5. Configurar armazenamento no novo projeto ==========
if storage_connections:
    for connection in storage_connections:
        try:
            new_project.connect_storage(
                storage_type=connection['storage_type'],
                **connection['storage_config']
            )
            print(f"✅ Armazenamento {connection['storage_type']} configurado no novo projeto")
        except Exception as e:
            print(f"⚠️ Erro ao configurar armazenamento {connection['storage_type']}: {str(e)}")

# ========== 6. Preparar tasks para importação ==========
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

# ========== 7. Importar tasks + annotations ==========
import_response = new_project.import_tasks(prepared_tasks)

print(f"🎉 Importação concluída. {len(import_response)} tasks importadas para projeto {new_project.id}")