import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { Mail, Lock, LogIn } from "lucide-react";

import { loginFormSchema } from "../../utils/userFormValidation";
import { login, clearError } from "../../state/slices/userSlice";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Alert from "../../components/ui/Alert";

const Login = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { status } = useSelector((state) => state.user);

  const [formData, setFormData] = useState({ username: "", password: "" });
  const [formErrors, setFormErrors] = useState({});
  const [loginError, setLoginError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.currentTarget;
    setFormData({ ...formData, [name]: value });
    setFormErrors({ ...formErrors, [name]: "" });
    setLoginError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoginError("");
    dispatch(clearError());

    try {
      await loginFormSchema.validate(formData, { abortEarly: false });
      await dispatch(login(formData)).unwrap();
      navigate("/home");
    } catch (err) {
      if (err?.inner) {
        const errors = {};
        err.inner.forEach((field) => {
          errors[field.path] = field.message;
        });
        setFormErrors(errors);
      } else if (typeof err === "string") {
        setLoginError(err);
      } else {
        setLoginError("Usuário ou senha inválidos");
      }
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-linear-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <span className="text-white text-2xl">🦷</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            Bem-vindo de volta
          </h1>
          <p className="text-gray-500 mt-1">
            Entre na sua conta para continuar
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
          <form noValidate onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Usuário"
              name="username"
              type="text"
              placeholder="Seu nome de usuário"
              icon={Mail}
              value={formData.username}
              onChange={handleChange}
              error={formErrors.username}
            />
            <Input
              label="Senha"
              name="password"
              type="password"
              placeholder="Sua senha"
              icon={Lock}
              value={formData.password}
              onChange={handleChange}
              error={formErrors.password}
            />
            {loginError && <Alert variant="error">{loginError}</Alert>}
            <Button
              type="submit"
              className="w-full"
              size="lg"
              loading={status === "loading"}
              icon={LogIn}
            >
              Entrar
            </Button>
          </form>
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          Não tem uma conta?{" "}
          <Link
            to="/register"
            className="text-primary-600 font-medium hover:text-primary-700"
          >
            Cadastre-se
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
