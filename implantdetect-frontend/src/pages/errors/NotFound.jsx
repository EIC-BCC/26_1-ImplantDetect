import { Link } from 'react-router-dom';
import { Home, Search } from 'lucide-react';
import Button from '../../components/ui/Button';

const NotFound = () => {
  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
      <div className="text-center animate-fade-in">
        <div className="text-8xl font-extrabold text-primary-200 mb-4">404</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Página não encontrada</h1>
        <p className="text-gray-500 mb-8 max-w-md mx-auto">
          A página que você está procurando não existe ou foi movida para outro endereço.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link to="/">
            <Button icon={Home}>Voltar ao Início</Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
