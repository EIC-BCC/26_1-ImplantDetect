import { useState, useEffect } from 'react';
import { Search, UserCheck, UserX, Shield, MoreVertical } from 'lucide-react';

import adminService from '../../state/services/adminService';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Input from '../../components/ui/Input';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Alert from '../../components/ui/Alert';

const roleColors = {
  user: 'blue',
  specialist: 'teal',
  admin: 'purple',
};

const roleLabels = {
  user: 'Usuário',
  specialist: 'Especialista',
  admin: 'Administrador',
};

const ROLES = ['user', 'specialist', 'admin'];

const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [actionMenu, setActionMenu] = useState(null);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        const data = await adminService.getUsers();
        setUsers(data);
      } catch (err) {
        setError(err?.detail || err?.message || 'Erro ao carregar usuários.');
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  const handleSetRole = async (userId, role) => {
    try {
      const updated = await adminService.setUserRole(userId, role);
      setUsers((prev) => prev.map((u) => (u.user_id === userId ? { ...u, ...updated } : u)));
    } catch (err) {
      setError(err?.detail || 'Erro ao alterar papel.');
    } finally {
      setActionMenu(null);
    }
  };

  const handleToggleActive = async (userId, currentActive) => {
    try {
      const updated = await adminService.setUserActive(userId, !currentActive);
      setUsers((prev) => prev.map((u) => (u.user_id === userId ? { ...u, ...updated } : u)));
    } catch (err) {
      setError(err?.detail || 'Erro ao alterar status.');
    } finally {
      setActionMenu(null);
    }
  };

  const filtered = users.filter(
    (u) =>
      u.username?.toLowerCase().includes(search.toLowerCase()) ||
      u.email?.toLowerCase().includes(search.toLowerCase())
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
          <h1 className="text-2xl font-bold text-gray-900">Gerenciar Usuários</h1>
          <p className="text-gray-500 mt-1">Visualize e gerencie as contas do sistema</p>
        </div>
        <div className="w-full sm:w-72">
          <Input
            placeholder="Buscar por nome ou email..."
            icon={Search}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {error && <Alert variant="error" className="mb-2">{error}</Alert>}

      {users.length === 0 && !error ? (
        <Card className="text-center py-16">
          <Alert variant="info">Nenhum usuário encontrado.</Alert>
        </Card>
      ) : (
        <Card padding={false}>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Usuário</th>
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">E-mail</th>
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Papel</th>
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map((user) => (
                  <tr key={user.user_id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-primary-700">
                            {user.username?.charAt(0)?.toUpperCase()}
                          </span>
                        </div>
                        <span className="font-medium text-gray-900">{user.username}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{user.email}</td>
                    <td className="px-6 py-4">
                      <Badge color={roleColors[user.role] || 'gray'} dot>
                        {roleLabels[user.role] || user.role}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      {user.active ? (
                        <span className="inline-flex items-center gap-1 text-sm text-green-600">
                          <UserCheck className="h-4 w-4" /> Ativo
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-sm text-red-500">
                          <UserX className="h-4 w-4" /> Inativo
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="relative inline-block">
                        <button
                          onClick={() => setActionMenu(actionMenu === user.user_id ? null : user.user_id)}
                          className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600"
                        >
                          <MoreVertical className="h-4 w-4" />
                        </button>
                        {actionMenu === user.user_id && (
                          <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border py-1 z-10 animate-fade-in">
                            {ROLES.filter((r) => r !== user.role).map((role) => (
                              <button
                                key={role}
                                onClick={() => handleSetRole(user.user_id, role)}
                                className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center gap-2"
                              >
                                <Shield className="h-4 w-4" /> Tornar {roleLabels[role]}
                              </button>
                            ))}
                            <button
                              onClick={() => handleToggleActive(user.user_id, user.active)}
                              className="w-full text-left px-4 py-2 text-sm hover:bg-red-50 text-red-600 flex items-center gap-2"
                            >
                              <UserX className="h-4 w-4" /> {user.active ? 'Desativar' : 'Ativar'}
                            </button>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};

export default AdminUsers;
