import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { useState } from 'react';

import { registrationFormSchema } from '../utils/userFormValidation';
import { register } from '../state/slices/userSlice';

const Register = () => {

    const navigate = useNavigate();
    const dispatch = useDispatch();

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: ''
    });

    const [formErrors, setFormErrors] = useState({
        username: '',
        email: '',
        password: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.currentTarget;
        setFormData({ ...formData, [name]: value });
        setFormErrors({ ...formErrors, [name]: null });
    }

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            await registrationFormSchema.validate(formData, { abortEarly: false });
            dispatch(register(formData)).then(() => {
                navigate('/');
            }).catch(err => {
                console.error(err);
            });
        } catch (err) {
            if (err.inner) {
                let errors = {};
                err.inner.forEach(field => {
                    errors[field.path] = field.message;
                });
                setFormErrors(errors);
            } else {
                console.error(err);
            }
        }
    }

    return (
        <>
            <main className="w-100 m-auto align-items-center" style={{ maxWidth: '330px', padding: '1rem' }}>
                <form noValidate onSubmit={handleSubmit}>
                    <div className="text-center">
                        <i className="bi bi-plus-circle" style={{ fontSize: '64px' }}></i>
                        <h1 className="h3 mb-3 fw-normal">Cadastrar-se</h1>
                    </div>
                    <div className="form-floating">
                        <input type="text" className={`form-control ${formErrors.username ? 'is-invalid' : ''}`} id="floatingInput" placeholder="Usuário" name="username" value={formData.username} onChange={handleChange} style={{ marginBottom: '-1px', borderBottomRightRadius: 0, borderBottomLeftRadius: 0 }} />
                        <label htmlFor="floatingInput">Usuário</label>
                        <div className="invalid-feedback">{formErrors.username}</div>
                    </div>
                    <div className="form-floating">
                        <input type="email" className={`form-control ${formErrors.email ? 'is-invalid' : ''}`} id="floatingInput" name="email" placeholder="Email" value={formData.email} onChange={handleChange} style={{ marginBottom: '-1px', borderRadius: 0 }} />
                        <label htmlFor="floatingInput">E-mail</label>
                        <div className="invalid-feedback">{formErrors.email}</div>
                    </div>
                    <div className="form-floating">
                        <input type="password" className={`form-control ${formErrors.password ? 'is-invalid' : ''}`} id="floatingPassword" name="password" placeholder="Senha" value={formData.password} onChange={handleChange} style={{ borderTopLeftRadius: 0, borderTopRightRadius: 0 }} />
                        <label htmlFor="floatingPassword">Senha</label>
                        <div className="invalid-feedback">{formErrors.password}</div>
                    </div>
                    <div className="text-start my-3">
                        <button className="w-100 btn btn-lg btn-outline-success" type="submit">Cadastrar-se</button>
                    </div>
                </form>
            </main>
        </>
    );
}

export default Register;