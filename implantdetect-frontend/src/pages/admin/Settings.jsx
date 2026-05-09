import { useState } from "react";
import { Save, Server, Shield, Image, Brain } from "lucide-react";

import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import Alert from "../../components/ui/Alert";

const AdminSettings = () => {
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="animate-fade-in space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Configurações do Sistema
        </h1>
        <p className="text-gray-500 mt-1">
          Gerencie as configurações gerais da plataforma
        </p>
      </div>

      {saved && (
        <Alert variant="success">Configurações salvas com sucesso!</Alert>
      )}

      {/* General Settings */}
      <Card>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
            <Server className="h-5 w-5 text-primary-600" />
          </div>
          <div>
            <Card.Title>Geral</Card.Title>
            <Card.Description>
              Configurações gerais do servidor
            </Card.Description>
          </div>
        </div>
        <form onSubmit={handleSave} className="space-y-4">
          <Input
            label="URL da API"
            placeholder="http://localhost:8000"
            defaultValue="http://localhost:8000"
            disabled
          />
          <Input
            label="Ambiente"
            placeholder="development"
            defaultValue="development"
            disabled
          />
          <div className="pt-2">
            <Button type="submit" icon={Save} size="md">
              Salvar
            </Button>
          </div>
        </form>
      </Card>

      {/* Security Settings */}
      <Card>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center">
            <Shield className="h-5 w-5 text-red-600" />
          </div>
          <div>
            <Card.Title>Segurança</Card.Title>
            <Card.Description>
              Configurações de autenticação e segurança
            </Card.Description>
          </div>
        </div>
        <form onSubmit={handleSave} className="space-y-4">
          <Input
            label="Tempo de expiração do token (minutos)"
            type="number"
            defaultValue="30"
          />
          <Input label="Algoritmo de hash" defaultValue="HS256" disabled />
          <div className="pt-2">
            <Button type="submit" icon={Save} size="md">
              Salvar
            </Button>
          </div>
        </form>
      </Card>

      {/* Image Settings */}
      <Card>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-accent-50 rounded-lg flex items-center justify-center">
            <Image className="h-5 w-5 text-accent-600" />
          </div>
          <div>
            <Card.Title>Upload de Imagens</Card.Title>
            <Card.Description>Limites e formatos aceitos</Card.Description>
          </div>
        </div>
        <form onSubmit={handleSave} className="space-y-4">
          <Input label="Tamanho máximo (MB)" type="number" defaultValue="50" />
          <Input
            label="Formatos suportados"
            defaultValue="JPG, JPEG, PNG"
            disabled
          />
          <div className="pt-2">
            <Button type="submit" icon={Save} size="md">
              Salvar
            </Button>
          </div>
        </form>
      </Card>

      {/* Model Settings */}
      <Card>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center">
            <Brain className="h-5 w-5 text-purple-600" />
          </div>
          <div>
            <Card.Title>Modelo de IA</Card.Title>
            <Card.Description>Configurações do modelo YOLO</Card.Description>
          </div>
        </div>
        <form onSubmit={handleSave} className="space-y-4">
          <Input
            label="Caminho do Modelo"
            defaultValue="yolo11m-obb.pt"
            disabled
          />
          <Input
            label="Confiança mínima"
            type="number"
            step="0.01"
            defaultValue="0.10"
          />
          <div className="pt-2">
            <Button type="submit" icon={Save} size="md">
              Salvar
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default AdminSettings;
