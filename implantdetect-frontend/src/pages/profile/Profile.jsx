import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { User, Mail, Lock, Save } from "lucide-react";

import { updateUser } from "../../state/slices/userSlice";
import useAuth from "../../hooks/useAuth";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Card from "../../components/ui/Card";
import Alert from "../../components/ui/Alert";
import Badge from "../../components/ui/Badge";

const roleLabels = {
  user: { label: "Usuário", color: "blue" },
  specialist: { label: "Especialista", color: "teal" },
  admin: { label: "Administrador", color: "purple" },
};

const Profile = () => {
  const dispatch = useDispatch();
  const { user } = useAuth();
  const { status } = useSelector((state) => state.user);

  const [formData, setFormData] = useState({
    username: user?.username || "",
    email: user?.email || "",
    password: "",
  });
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.currentTarget;
    setFormData({ ...formData, [name]: value });
    setSuccess("");
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccess("");
    setError("");

    try {
      const payload = { user_id: user?.user_id };
      if (formData.username !== user?.username)
        payload.username = formData.username;
      if (formData.email !== user?.email) payload.email = formData.email;
      if (formData.password) payload.password = formData.password;

      await dispatch(updateUser(payload)).unwrap();
      setSuccess("Perfil atualizado com sucesso!");
      setFormData((prev) => ({ ...prev, password: "" }));
    } catch (err) {
      setError(typeof err === "string" ? err : "Erro ao atualizar perfil.");
    }
  };

  const roleInfo = roleLabels[user?.role] || roleLabels.user;

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Meu Perfil</h1>

      {/* User Info Card */}
      <Card className="mb-8">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-linear-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center shrink-0">
            <User className="h-8 w-8 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {user?.username || "Usuário"}
            </h2>
            <p className="text-gray-500 text-sm">{user?.email || ""}</p>
            <div className="mt-1">
              <Badge color={roleInfo.color} dot>
                {roleInfo.label}
              </Badge>
            </div>
          </div>
        </div>
      </Card>

      {/* Edit Form */}
      <Card>
        <Card.Header>
          <Card.Title>Editar Informações</Card.Title>
          <Card.Description>
            Atualize seus dados de perfil abaixo.
          </Card.Description>
        </Card.Header>

        <form onSubmit={handleSubmit} className="space-y-5">
          <Input
            label="Usuário"
            name="username"
            type="text"
            placeholder="Seu nome de usuário"
            icon={User}
            value={formData.username}
            onChange={handleChange}
          />

          <Input
            label="E-mail"
            name="email"
            type="email"
            placeholder="seu@email.com"
            icon={Mail}
            value={formData.email}
            onChange={handleChange}
          />

          <Input
            label="Nova Senha (deixe em branco para manter)"
            name="password"
            type="password"
            placeholder="Nova senha"
            icon={Lock}
            value={formData.password}
            onChange={handleChange}
          />

          {success && <Alert variant="success">{success}</Alert>}
          {error && <Alert variant="error">{error}</Alert>}

          <Button
            type="submit"
            size="lg"
            className="w-full"
            loading={status === "loading"}
            icon={Save}
          >
            Salvar Alterações
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default Profile;
