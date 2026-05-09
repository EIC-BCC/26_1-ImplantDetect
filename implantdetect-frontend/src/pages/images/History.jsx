import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Eye,
  Loader2,
} from "lucide-react";

import ImageService from "../../state/services/imageService";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import Alert from "../../components/ui/Alert";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";

const statusConfig = {
  Pendente: { icon: Clock, color: "amber", badgeColor: "amber" },
  Executando: { icon: Loader2, color: "blue", badgeColor: "blue" },
  Concluído: { icon: CheckCircle, color: "green", badgeColor: "green" },
  Falhou: { icon: XCircle, color: "red", badgeColor: "red" },
  Cancelado: { icon: AlertTriangle, color: "gray", badgeColor: "gray" },
};

const History = () => {
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProcesses = async () => {
      setLoading(true);
      try {
        const data = await ImageService.getUserProcesses();
        setProcesses(
          data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)),
        );
      } catch (err) {
        setError(err?.detail || err?.message || "Erro ao carregar histórico.");
      } finally {
        setLoading(false);
      }
    };
    fetchProcesses();
  }, []);

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("pt-BR", {
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="text-gray-500 mt-4">Carregando histórico...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Histórico de Análises
        </h1>
        <p className="text-gray-500 mt-1">
          Acompanhe todas as suas análises de radiografias
        </p>
      </div>

      {error && (
        <Alert variant="error" className="mb-6">
          {error}
        </Alert>
      )}

      {processes.length === 0 && !error ? (
        <Card className="text-center py-16">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Clock className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Nenhuma análise encontrada
          </h3>
          <p className="text-gray-500 mb-6">
            Você ainda não enviou nenhuma imagem para análise.
          </p>
          <Link
            to="/images/upload"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            Enviar primeira imagem
          </Link>
        </Card>
      ) : (
        <div className="space-y-4">
          {processes.map((process) => {
            const config = statusConfig[process.status_name] ?? {
              icon: Clock,
              color: "gray",
              badgeColor: "gray",
            };
            const StatusIcon = config.icon;

            return (
              <Card key={process.process_id} hover className="group">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center bg-${config.color}-50`}
                    >
                      <StatusIcon
                        className={`h-5 w-5 text-${config.color}-600`}
                      />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-gray-900">
                          Análise #{process.process_id}
                        </h3>
                        <Badge color={config.badgeColor} dot>
                          {process.status_name}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-500 mt-0.5">
                        Criado em {formatDate(process.created_at)}
                      </p>
                    </div>
                  </div>

                  <Link
                    to={`/process/${process.process_id}/results`}
                    className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors group-hover:text-primary-700"
                  >
                    <Eye className="h-4 w-4" />
                    Ver Resultados
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default History;
