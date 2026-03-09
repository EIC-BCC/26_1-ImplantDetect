import { Link } from 'react-router-dom';
import { Upload, History, BarChart3, ArrowRight } from 'lucide-react';
import useAuth from '../../hooks/useAuth';
import Card from '../../components/ui/Card';

const quickActions = [
  {
    icon: Upload,
    title: 'Enviar Raio X',
    description: 'Faça upload de uma nova imagem para análise por IA.',
    to: '/images/upload',
    color: 'bg-primary-50 text-primary-600',
  },
  {
    icon: History,
    title: 'Histórico',
    description: 'Veja todas as suas análises anteriores.',
    to: '/history',
    color: 'bg-accent-50 text-accent-600',
  },
  {
    icon: BarChart3,
    title: 'Última Análise',
    description: 'Confira os resultados da última imagem processada.',
    to: '/history',
    color: 'bg-purple-50 text-purple-600',
  },
];

const Home = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-gray-900">
          Olá{user?.username ? `, ${user.username}` : ''}! 👋
        </h1>
        <p className="text-gray-500 mt-2 text-lg">
          Bem-vindo ao ImplantDetect. O que deseja fazer hoje?
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {quickActions.map((action, index) => (
          <Link key={index} to={action.to}>
            <Card hover className="h-full group">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${action.color}`}>
                <action.icon className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">
                {action.title}
              </h3>
              <p className="text-gray-500 text-sm mb-4">{action.description}</p>
              <div className="flex items-center text-primary-600 text-sm font-medium">
                Acessar <ArrowRight className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </Card>
          </Link>
        ))}
      </div>

      <div className="bg-linear-to-r from-primary-600 to-accent-600 rounded-2xl p-8 text-white">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
          <div>
            <h2 className="text-2xl font-bold mb-2">Detecção com YOLOv11</h2>
            <p className="text-white/80 max-w-lg">
              Nossa plataforma utiliza o modelo YOLOv11 treinado especificamente para detectar
              e classificar diferentes tipos de implantes dentários em radiografias panorâmicas.
            </p>
          </div>
          <Link to="/images/upload">
            <button className="bg-white text-primary-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors shadow-lg flex items-center gap-2 whitespace-nowrap">
              <Upload className="h-5 w-5" />
              Analisar Imagem
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
