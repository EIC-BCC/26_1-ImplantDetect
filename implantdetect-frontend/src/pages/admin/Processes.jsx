import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Eye } from 'lucide-react';

import adminService from '../../state/services/adminService';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Input from '../../components/ui/Input';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Alert from '../../components/ui/Alert';

const statusConfig = {
  Pendente: { color: 'amber' },
  Executando: { color: 'blue' },
  'Concluído': { color: 'green' },
  Falhou: { color: 'red' },
  Cancelado: { color: 'gray' },
};

const AdminProcesses = () => {
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchProcesses = async () => {
      setLoading(true);
      try {
        const data = await adminService.getProcesses();
        setProcesses(data);
      } catch (err) {
        setError(err?.detail || err?.message || 'Erro ao carregar processos.');
      } finally {
        setLoading(false);
      }
    };
    fetchProcesses();
  }, []);

  const formatDate = (dateStr) => {
    try {
      return new Date(dateStr).toLocaleDateString('pt-BR', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
      });
    } catch { return dateStr; }
  };

  const filtered = processes.filter(
    (p) =>
      String(p.process_id).includes(search) ||
      p.status_name?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gerenciar Processos</h1>
          <p className="text-gray-500 mt-1">Acompanhe todos os processos de análise do sistema</p>
        </div>
        <div className="w-full sm:w-72">
          <Input
            placeholder="Buscar por ID ou status..."
            icon={Search}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {error && <Alert variant="error" className="mb-2">{error}</Alert>}

      {processes.length === 0 && !error ? (
        <Card className="text-center py-16">
          <Alert variant="info">Nenhum processo encontrado.</Alert>
        </Card>
      ) : (
        <Card padding={false}>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Usuário</th>
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Data</th>
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map((process) => {
                  const config = statusConfig[process.status_name] ?? { color: 'gray' };
                  return (
                    <tr key={process.process_id} className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-6 py-4 font-medium text-gray-900">#{process.process_id}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">Usuário #{process.user_id}</td>
                      <td className="px-6 py-4">
                        <Badge color={config.color} dot>{process.status_name}</Badge>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">{formatDate(process.created_at)}</td>
                      <td className="px-6 py-4 text-right">
                        <Link
                          to={`/process/${process.process_id}/results`}
                          className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-medium"
                        >
                          <Eye className="h-4 w-4" /> Ver
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};

export default AdminProcesses;
