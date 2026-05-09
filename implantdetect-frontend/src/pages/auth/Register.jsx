import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { User, Mail, Lock, UserPlus } from "lucide-react";

import { registrationFormSchema } from "../../utils/userFormValidation";
import { register } from "../../state/slices/userSlice";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Alert from "../../components/ui/Alert";

const Register = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { status } = useSelector((state) => state.user);

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [formErrors, setFormErrors] = useState({});
  const [registerError, setRegisterError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.currentTarget;
    setFormData({ ...formData, [name]: value });
    setFormErrors({ ...formErrors, [name]: "" });
    setRegisterError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setRegisterError("");

    try {
      await registrationFormSchema.validate(formData, { abortEarly: false });
      await dispatch(register(formData)).unwrap();
      navigate("/login");
    } catch (err) {
      if (err?.inner) {
        const errors = {};
        err.inner.forEach((field) => {
          errors[field.path] = field.message;
        });
        setFormErrors(errors);
      } else if (typeof err === "string") {
        setRegisterError(err);
      } else {
        setRegisterError(err?.message || "Erro ao registrar. Tente novamente.");
      }
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-linear-to-br from-accent-500 to-primary-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <UserPlus className="text-white h-8 w-8" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Criar Conta</h1>
          <p className="text-gray-500 mt-1">
            Cadastre-se para começar a usar o ImplantDetect
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
          <form noValidate onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Usuário"
              name="username"
              type="text"
              placeholder="Escolha um nome de usuário"
              icon={User}
              value={formData.username}
              onChange={handleChange}
              error={formErrors.username}
              disabled={status === "loading"}
            />
            <Input
              label="E-mail"
              name="email"
              type="email"
              placeholder="seu@email.com"
              icon={Mail}
              value={formData.email}
              onChange={handleChange}
              error={formErrors.email}
              disabled={status === "loading"}
            />
            <Input
              label="Senha"
              name="password"
              type="password"
              placeholder="Crie uma senha segura"
              icon={Lock}
              value={formData.password}
              onChange={handleChange}
              error={formErrors.password}
              disabled={status === "loading"}
            />
            {registerError && <Alert variant="error">{registerError}</Alert>}
            <Button
              type="submit"
              className="w-full"
              size="lg"
              loading={status === "loading"}
              icon={UserPlus}
            >
              {status === "loading" ? "Cadastrando..." : "Cadastrar"}
            </Button>
          </form>
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          Já tem uma conta?{" "}
          <Link
            to="/login"
            className="text-primary-600 font-medium hover:text-primary-700"
          >
            Entrar
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
