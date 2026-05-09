import { Link } from "react-router-dom";
import { Home, RefreshCw } from "lucide-react";
import Button from "../../components/ui/Button";

const ServerError = () => {
  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
      <div className="text-center animate-fade-in">
        <div className="text-8xl font-extrabold text-red-200 mb-4">500</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Erro interno do servidor
        </h1>
        <p className="text-gray-500 mb-8 max-w-md mx-auto">
          Algo deu errado em nosso servidor. Por favor, tente novamente mais
          tarde ou entre em contato com o suporte se o problema persistir.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button icon={RefreshCw} onClick={() => window.location.reload()}>
            Tentar Novamente
          </Button>
          <Link to="/">
            <Button variant="secondary" icon={Home}>
              Voltar ao Início
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ServerError;
