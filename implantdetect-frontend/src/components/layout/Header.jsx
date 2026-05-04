import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Menu, X, Upload, History, User, LogOut, LogIn, UserPlus,
  LayoutDashboard, Home, ChevronDown
} from 'lucide-react';

const Header = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const token = useSelector((state) => state.user.token);
  const user = useSelector((state) => state.user.user);
  const location = useLocation();

  const isLanding = location.pathname === '/';

  const isActive = (path) => location.pathname === path;

  const navLinkClass = (path) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
      isActive(path)
        ? 'bg-primary-50 text-primary-700'
        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
    }`;

  return (
    <header className={`sticky top-0 z-50 ${isLanding ? 'bg-white/80 backdrop-blur-md' : 'bg-white'} border-b border-gray-200`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to={token ? '/home' : '/'} className="flex items-center gap-2 group">
            <div className="w-9 h-9 bg-linear-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
              <span className="text-white text-lg">🦷</span>
            </div>
            <span className="text-lg font-bold text-gray-900">
              Implant<span className="text-primary-600">Detect</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {token ? (
              <>
                <Link to="/home" className={navLinkClass('/home')}>
                  <Home className="h-4 w-4" />
                  Início
                </Link>
                <Link to="/images/upload" className={navLinkClass('/images/upload')}>
                  <Upload className="h-4 w-4" />
                  Enviar Raio X
                </Link>
                <Link to="/history" className={navLinkClass('/history')}>
                  <History className="h-4 w-4" />
                  Histórico
                </Link>

                {/* User dropdown */}
                <div className="relative ml-2">
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    onBlur={() => setTimeout(() => setDropdownOpen(false), 200)}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-7 h-7 bg-primary-100 rounded-full flex items-center justify-center">
                      <User className="h-4 w-4 text-primary-600" />
                    </div>
                    <span className="hidden lg:inline">{user?.username || 'Minha Conta'}</span>
                    <ChevronDown className={`h-4 w-4 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
                  </button>

                  {dropdownOpen && (
                    <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 animate-fade-in">
                      <Link to="/profile" className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                        <User className="h-4 w-4" /> Perfil
                      </Link>
                      {user?.role === 'admin' && (
                        <Link to="/admin" className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
                          <LayoutDashboard className="h-4 w-4" /> Painel Admin
                        </Link>
                      )}
                      <hr className="my-1 border-gray-100" />
                      <Link to="/logout" className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50">
                        <LogOut className="h-4 w-4" /> Sair
                      </Link>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <Link to="/login" className={navLinkClass('/login')}>
                  <LogIn className="h-4 w-4" />
                  Entrar
                </Link>
                <Link
                  to="/register"
                  className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-primary-600 text-white hover:bg-primary-700 transition-colors shadow-sm"
                >
                  <UserPlus className="h-4 w-4" />
                  Cadastrar
                </Link>
              </>
            )}
          </nav>

          {/* Mobile toggle */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          >
            {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Nav */}
        {mobileOpen && (
          <div className="md:hidden pb-4 border-t border-gray-100 mt-2 pt-3 animate-fade-in">
            <nav className="flex flex-col gap-1">
              {token ? (
                <>
                  <Link to="/home" className={navLinkClass('/home')} onClick={() => setMobileOpen(false)}>
                    <Home className="h-4 w-4" /> Início
                  </Link>
                  <Link to="/images/upload" className={navLinkClass('/images/upload')} onClick={() => setMobileOpen(false)}>
                    <Upload className="h-4 w-4" /> Enviar Raio X
                  </Link>
                  <Link to="/history" className={navLinkClass('/history')} onClick={() => setMobileOpen(false)}>
                    <History className="h-4 w-4" /> Histórico
                  </Link>
                  <Link to="/profile" className={navLinkClass('/profile')} onClick={() => setMobileOpen(false)}>
                    <User className="h-4 w-4" /> Perfil
                  </Link>
                  {user?.role === 'admin' && (
                    <Link to="/admin" className={navLinkClass('/admin')} onClick={() => setMobileOpen(false)}>
                      <LayoutDashboard className="h-4 w-4" /> Painel Admin
                    </Link>
                  )}
                  <hr className="my-2 border-gray-100" />
                  <Link to="/logout" className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50">
                    <LogOut className="h-4 w-4" /> Sair
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/login" className={navLinkClass('/login')} onClick={() => setMobileOpen(false)}>
                    <LogIn className="h-4 w-4" /> Entrar
                  </Link>
                  <Link to="/register" className={navLinkClass('/register')} onClick={() => setMobileOpen(false)}>
                    <UserPlus className="h-4 w-4" /> Cadastrar
                  </Link>
                </>
              )}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
