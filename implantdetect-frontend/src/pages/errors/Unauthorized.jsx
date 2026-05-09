import { Link } from "react-router-dom";
import { Home, ShieldX } from "lucide-react";
import Button from "../../components/ui/Button";

const Unauthorized = () => {
  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
      <div className="text-center animate-fade-in">
        <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <ShieldX className="h-10 w-10 text-red-500" />
        </div>
        <div className="text-6xl font-extrabold text-red-200 mb-4">403</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Acesso negado</h1>
        <p className="text-gray-500 mb-8 max-w-md mx-auto">
          Você não tem permissão para acessar esta página. Se acredita que isso
          é um erro, entre em contato com o administrador.
        </p>
        <Link to="/">
          <Button icon={Home}>Voltar ao Início</Button>
        </Link>
      </div>
    </div>
  );
};

export default Unauthorized;
