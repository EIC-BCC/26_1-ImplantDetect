import { Users, Activity, CheckCircle, AlertTriangle, TrendingUp, Clock } from 'lucide-react';
import Card from '../../components/ui/Card';

const statCards = [
  {
    label: 'Usuários Ativos',
    value: '—',
    icon: Users,
    color: 'bg-primary-50 text-primary-600',
    trend: null,
  },
  {
    label: 'Análises Realizadas',
    value: '—',
    icon: Activity,
    color: 'bg-accent-50 text-accent-600',
    trend: null,
  },
  {
    label: 'Taxa de Sucesso',
    value: '—',
    icon: CheckCircle,
    color: 'bg-green-50 text-green-600',
    trend: null,
  },
  {
    label: 'Falhas Recentes',
    value: '—',
    icon: AlertTriangle,
    color: 'bg-red-50 text-red-600',
    trend: null,
  },
];

const AdminDashboard = () => {
  return (
    <div className="animate-fade-in space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Painel Administrativo</h1>
        <p className="text-gray-500 mt-1">Visão geral do sistema ImplantDetect</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} hover>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                {stat.trend && (
                  <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
                    <TrendingUp className="h-4 w-4" />
                    <span>{stat.trend}</span>
                  </div>
                )}
              </div>
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${stat.color}`}>
                <stat.icon className="h-6 w-6" />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <Card.Header>
            <Card.Title>Atividade Recente</Card.Title>
            <Card.Description>Últimos processos no sistema</Card.Description>
          </Card.Header>
          <div className="space-y-4">
            <div className="flex items-center justify-center py-12 text-gray-400">
              <div className="text-center">
                <Clock className="h-8 w-8 mx-auto mb-2" />
                <p className="text-sm">Os dados serão carregados da API</p>
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <Card.Header>
            <Card.Title>Resumo do Sistema</Card.Title>
            <Card.Description>Status dos componentes</Card.Description>
          </Card.Header>
          <div className="space-y-3">
            {[
              { name: 'API Backend', status: 'Operacional', color: 'bg-green-500' },
              { name: 'Banco de Dados', status: 'Operacional', color: 'bg-green-500' },
              { name: 'Modelo YOLO', status: 'Carregado', color: 'bg-green-500' },
              { name: 'Upload de Imagens', status: 'Disponível', color: 'bg-green-500' },
            ].map((item, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <span className="text-sm font-medium text-gray-700">{item.name}</span>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${item.color}`} />
                  <span className="text-sm text-gray-500">{item.status}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;
