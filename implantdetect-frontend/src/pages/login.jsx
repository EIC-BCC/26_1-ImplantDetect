import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useDispatch } from 'react-redux';

import { loginFormSchema } from '../utils/userFormValidation';
import { login } from '../state/slices/userSlice';

const Login = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch();

    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });

    const [formErrors, setFormErrors] = useState({
        username: '',
        password: ''
    });

    const [loginError, setLoginError] = useState(''); 

    const handleChange = (e) => {
        const { name, value } = e.currentTarget;
        setFormData({ ...formData, [name]: value });
        setFormErrors({ ...formErrors, [name]: null });
        setLoginError(''); 
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoginError(''); 

        try {
            await loginFormSchema.validate(formData, { abortEarly: false });

            dispatch(login(formData))
                .unwrap()
                .then(() => {
                    navigate('/home');
                })
                .catch(() => {
                    setLoginError('Invalid username or password');
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
    };

    return (
        <>
            <main className="w-100 m-auto align-items-center" style={{ maxWidth: '330px', padding: '1rem' }}>
                <form noValidate onSubmit={handleSubmit}>
                    <div className="text-center">
                        <i className="bi bi-person-circle" style={{ fontSize: '64px' }}></i>
                        <h1 className="h3 mb-3 fw-normal">Login</h1>
                    </div>
                    <div className="form-floating">
                        <input
                            type="text"
                            className={`form-control ${formErrors.username ? 'is-invalid' : ''}`}
                            id="floatingInput"
                            placeholder="Username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            style={{ marginBottom: '-1px', borderBottomRightRadius: 0, borderBottomLeftRadius: 0 }}
                        />
                        <label htmlFor="floatingInput">Username</label>
                        <div className="invalid-feedback">{formErrors.username}</div>
                    </div>
                    <div className="form-floating">
                        <input
                            type="password"
                            className={`form-control ${formErrors.password ? 'is-invalid' : ''}`}
                            id="floatingPassword"
                            name="password"
                            placeholder="Password"
                            value={formData.password}
                            onChange={handleChange}
                            style={{ borderTopLeftRadius: 0, borderTopRightRadius: 0 }}
                        />
                        <label htmlFor="floatingPassword">Password</label>
                        <div className="invalid-feedback">{formErrors.password}</div>
                    </div>

                    
                    {loginError && (
                        <div className="alert alert-danger text-center mt-3" role="alert">
                            {loginError}
                        </div>
                    )}

                    <div className="text-start my-3">
                        <button className="w-100 btn btn-lg btn-outline-success" type="submit">Login</button>
                    </div>

                    <div className="text-center">
                        <a href="/register" className="text-decoration-none">
                            Don’t have an account? Register
                        </a>
                    </div>
                </form>
            </main>
        </>
    );
};

export default Login;
