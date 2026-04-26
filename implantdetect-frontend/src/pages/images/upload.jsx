import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageService from '../../state/services/imageService';
import { imageFormSchema } from '../../utils/imageFormValidation';

const ImageUpload = () => {
    const [formData, setFormData] = useState({
        file: null
    });

    const [formErrors, setFormErrors] = useState({
        file: ''
    });

    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value, files } = e.currentTarget;
        if (files) {
            if (name === 'file') {
                const file = files[0];
                setFormData({ ...formData, [name]: file });
            } else {
                setFormData({ ...formData, [name]: files[0] });
            }
        } else {
            setFormData({ ...formData, [name]: value });
        }

        setFormErrors({ ...formErrors, [name]: null });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            await imageFormSchema.validate(formData, { abortEarly: false });

            const submitData = new FormData();
            submitData.append('image', formData.file);

            const response = await ImageService.upload(submitData);
            if (response?.process_id) {
                navigate(`/process/${response.process_id}/results`);
            } else {
                setFormErrors({ file: 'Processo criado, mas não foi possível obter o ID do processo.' });
            }
        } catch (err) {
            if (err && err.inner) {
                let errors = {};
                err.inner.forEach(field => {
                    errors[field.path] = field.message;
                });
                setFormErrors(errors);
            } else if (err && err.detail) {
                setFormErrors({ file: err.detail || 'Erro ao enviar imagem.' });
            } else if (typeof err === 'string') {
                setFormErrors({ file: err });
            } else {
                setFormErrors({ file: 'Erro inesperado ao enviar imagem.' });
                console.error(err);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container" style={{ maxWidth: '48em', margin: '0 auto', padding: '3em 1em' }}>
            <main>
                <h1 className="text-center">Upload de Imagem</h1>
                <p className="lead text-center">Envie a imagem de Raio X para análise.</p>
                <form noValidate onSubmit={handleSubmit}>
                    <div className="form-floating mb-3">
                        <input type="file" className={`form-control ${formErrors.file ? 'is-invalid' : ''}`} id="floatingFile" name="file" accept=".jpg, .jpeg, .png" onChange={handleChange} />
                        <label htmlFor="floatingInput">Arquivo</label>
                        <div className="invalid-feedback">{formErrors.file}</div>
                    </div>
                    <div className="text-start my-3">
                        <button className="w-100 btn btn-lg btn-outline-success" type="submit" disabled={loading}>
                            {loading ? 'Enviando...' : 'Enviar'}
                        </button>
                    </div>
                </form>
            </main>
        </div>
    );
}

export default ImageUpload;
