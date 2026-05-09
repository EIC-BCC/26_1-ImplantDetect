import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Users,
  Activity,
  CheckCircle,
  AlertTriangle,
  Clock,
  Loader2,
  ArrowRight,
} from "lucide-react";

import adminService from "../../state/services/adminService";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import Alert from "../../components/ui/Alert";

const STATUS_COLORS = {
  Pendente: "amber",
  Executando: "blue",
  Concluído: "green",
  Falhou: "red",
  Cancelado: "gray",
};

const formatDate = (dateStr) => {
  try {
    return new Date(dateStr).toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateStr;
  }
};

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetch = async () => {
      try {
        const [u, p] = await Promise.all([
          adminService.getUsers(),
          adminService.getProcesses(),
        ]);
        setUsers(u);
        setProcesses(p);
      } catch (err) {
        setError(
          err?.detail || err?.message || "Erro ao carregar dados do painel.",
        );
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, []);

  const totalUsers = users.length;
  const activeUsers = users.filter((u) => u.active).length;
  const totalProcesses = processes.length;
  const completed = processes.filter(
    (p) => p.status_name === "Concluído",
  ).length;
  const failed = processes.filter((p) => p.status_name === "Falhou").length;
  const successRate =
    totalProcesses > 0 ? ((completed / totalProcesses) * 100).toFixed(1) : "—";

  const recentProcesses = [...processes]
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 8);

  const statCards = [
    {
      label: "Usuários Cadastrados",
      value: loading ? "—" : totalUsers,
      sub: loading ? "" : `${activeUsers} ativos`,
      icon: Users,
      color: "bg-primary-50 text-primary-600",
    },
    {
      label: "Análises Realizadas",
      value: loading ? "—" : totalProcesses,
      sub: loading ? "" : `${completed} concluídas`,
      icon: Activity,
      color: "bg-accent-50 text-accent-600",
    },
    {
      label: "Taxa de Sucesso",
      value: loading ? "—" : `${successRate}%`,
      sub: loading ? "" : `${completed} de ${totalProcesses}`,
      icon: CheckCircle,
      color: "bg-green-50 text-green-600",
    },
    {
      label: "Falhas",
      value: loading ? "—" : failed,
      sub: loading ? "" : "total acumulado",
      icon: AlertTriangle,
      color: "bg-red-50 text-red-600",
    },
  ];

  return (
    <div className="animate-fade-in space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Painel Administrativo
        </h1>
        <p className="text-gray-500 mt-1">
          Visão geral do sistema ImplantDetect
        </p>
      </div>

      {error && <Alert variant="error">{error}</Alert>}

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">
                  {stat.label}
                </p>
                {loading ? (
                  <div className="mt-2">
                    <Loader2 className="h-6 w-6 animate-spin text-gray-300" />
                  </div>
                ) : (
                  <>
                    <p className="text-3xl font-bold text-gray-900 mt-1">
                      {stat.value}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">{stat.sub}</p>
                  </>
                )}
              </div>
              <div
                className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${stat.color}`}
              >
                <stat.icon className="h-6 w-6" />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent processes + user breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <Card.Header>
              <Card.Title>Atividade Recente</Card.Title>
              <Card.Description>
                Últimos 8 processos no sistema
              </Card.Description>
            </Card.Header>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <LoadingSpinner size="md" />
              </div>
            ) : recentProcesses.length === 0 ? (
              <div className="flex items-center justify-center py-12 text-gray-400">
                <div className="text-center">
                  <Clock className="h-8 w-8 mx-auto mb-2" />
                  <p className="text-sm">Nenhum processo encontrado</p>
                </div>
              </div>
            ) : (
              <div className="divide-y divide-gray-50">
                {recentProcesses.map((p) => (
                  <div
                    key={p.process_id}
                    className="flex items-center justify-between py-3 gap-4"
                  >
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        Processo #{p.process_id}
                        <span className="text-gray-400 font-normal ml-2 text-xs">
                          usuário #{p.user_id}
                        </span>
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {formatDate(p.created_at)}
                      </p>
                    </div>
                    <Badge color={STATUS_COLORS[p.status_name] ?? "gray"} dot>
                      {p.status_name}
                    </Badge>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-4 pt-4 border-t border-gray-50">
              <Link
                to="/admin/processes"
                className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Ver todos os processos <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </Card>
        </div>

        <div>
          <Card className="h-full">
            <Card.Header>
              <Card.Title>Distribuição de Papéis</Card.Title>
              <Card.Description>Usuários por tipo de acesso</Card.Description>
            </Card.Header>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <LoadingSpinner size="md" />
              </div>
            ) : (
              <div className="space-y-3">
                {[
                  {
                    role: "admin",
                    label: "Administradores",
                    color: "bg-red-100 text-red-700",
                  },
                  {
                    role: "specialist",
                    label: "Especialistas",
                    color: "bg-accent-100 text-accent-700",
                  },
                  {
                    role: "user",
                    label: "Usuários",
                    color: "bg-primary-100 text-primary-700",
                  },
                ].map(({ role, label, color }) => {
                  const count = users.filter((u) => u.role === role).length;
                  const pct = totalUsers > 0 ? (count / totalUsers) * 100 : 0;
                  return (
                    <div key={role}>
                      <div className="flex items-center justify-between mb-1">
                        <span
                          className={`text-xs font-semibold px-2 py-0.5 rounded-full ${color}`}
                        >
                          {label}
                        </span>
                        <span className="text-sm font-bold text-gray-900">
                          {count}
                        </span>
                      </div>
                      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary-400 rounded-full transition-all duration-500"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}

                <div className="pt-4 border-t border-gray-50 mt-2">
                  <Link
                    to="/admin/users"
                    className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Gerenciar usuários <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
