import { useState } from 'react';
import ImageService from '../../state/services/imageService';
import { imageFormSchema } from '../../utils/imageFormValidation';

const ImageUpload = () => {
   
    const [formData, setFormData] = useState({
        file: null
    });

    const [formErrors, setFormErrors] = useState({
        file: ''
    });

    const [uploadUrl, setUploadUrl] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);

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

        try {
            await imageFormSchema.validate(formData, { abortEarly: false });

            const submitData = new FormData();
            submitData.append('file', formData.file);
            submitData.append('expiry_date', formData.expiry_date);

            const response = await ImageService.upload(submitData);
            setUploadUrl(response.upload_url);
            setIsModalOpen(true);
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

    const closeModal = (copy) => {
        if (copy) {
            navigator.clipboard.writeText(uploadUrl);
        }
        setFormData({ file: null });
        setIsModalOpen(false);
    };

    return (
        <div className="container" style={{ maxWidth: '48em', margin: '0 auto', padding: '3em 1em' }}>
            <main>
                <h1 className="text-center">Upload de Imagem</h1>
                <p className="lead text-center">Envie a imagem de Raio X para análise.</p>
                <form noValidate onSubmit={handleSubmit}>
                    <div className="form-floating mb-3">
                        <input type="file" className={`form-control ${formErrors.file ? 'is-invalid' : ''}`} id="floatingFile" name="file" accept=".jpg, .jpeg, .png, .pdf, .txt" onChange={handleChange} />
                        <label htmlFor="floatingInput">Arquivo</label>
                        <div className="invalid-feedback">{formErrors.file}</div>
                    </div>
                    <div className="text-start my-3">
                        <button className="w-100 btn btn-lg btn-outline-success" type="submit">Enviar</button>
                    </div>
                </form>

                {isModalOpen && (
                    <div className="modal show" style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 1050 }}>
                        <div className="modal-dialog" style={{ margin: 'auto', marginTop: '10%', maxWidth: '500px' }}>
                            <div className="modal-content">
                                <div className="modal-header">
                                    <h5 className="modal-title">Your File has been uploaded!</h5>
                                    <button type="button" className="btn-close" onClick={() => closeModal(false)} aria-label="Close"></button>
                                </div>
                                <div className="modal-body">
                                    <p>
                                        O arquivo foi enviado com sucesso!<br />
                                        Você pode acessar o arquivo enviado através do seguinte link:<br />
                                        URL: <a href={uploadUrl} target="_blank" rel="noopener noreferrer">{uploadUrl}</a><br />
                                    </p>
                                </div>
                                <div className="modal-footer">
                                    <button type="button" className="btn btn-secondary" onClick={() => closeModal(false)}>Fechar</button>
                                    <button type="button" className="btn btn-primary" onClick={() => closeModal(true)}>Copiar para a Área de Transferência</button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default ImageUpload;
