import * as yup from 'yup';

export const loginFormSchema = yup.object().shape({
    username: yup.string().required('Usuário é obrigatório'),
    password: yup.string().required('Senha é obrigatória')
});

export const registrationFormSchema = yup.object().shape({
    email: yup.string().email('Email inválido').required('Email é obrigatório').matches(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/, 'Email inválido.'),
    username: yup.string().required('Usuário é obrigatório'),
    password: yup.string().required('Senha é obrigatória')
});