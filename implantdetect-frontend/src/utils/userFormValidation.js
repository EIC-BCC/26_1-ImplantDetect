import * as yup from "yup";

export const loginFormSchema = yup.object().shape({
  username: yup.string().required("Usuário é obrigatório"),
  password: yup.string().required("Senha é obrigatória"),
});

const passwordRules = yup
  .string()
  .required("Senha é obrigatória")
  .min(8, "A senha deve ter ao menos 8 caracteres")
  .max(128, "A senha não pode ter mais de 128 caracteres")
  .matches(/[a-zA-Z]/, "A senha deve conter ao menos uma letra")
  .matches(/[0-9]/, "A senha deve conter ao menos um número");

export const registrationFormSchema = yup.object().shape({
  email: yup
    .string()
    .email("Email inválido")
    .required("Email é obrigatório")
    .max(254, "Email muito longo")
    .matches(
      /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      "Email inválido.",
    ),
  username: yup
    .string()
    .required("Usuário é obrigatório")
    .min(3, "O usuário deve ter ao menos 3 caracteres")
    .max(50, "O usuário não pode ter mais de 50 caracteres"),
  password: passwordRules,
});

export const updatePasswordSchema = yup.object().shape({
  password: passwordRules,
});
