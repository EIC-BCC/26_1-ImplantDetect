import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ImageService from '../../state/services/imageService';

const ImageResults = () => {
    const { process_id } = useParams();
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchResults = async () => {
            setLoading(true);
            setError('');
            try {
                const data = await ImageService.getProcessResults(process_id);
                setResults(data);
            } catch (err) {
                setError('Erro ao buscar resultados do processo: ' + (err.message || 'Erro desconhecido'));
                console.error('Error fetching process results:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchResults();
    }, [process_id]);

    return (
        <div className="container" style={{ maxWidth: '48em', margin: '0 auto', padding: '3em 1em' }}>
            <main>
                <h2 className="text-center" style={{ marginBottom: '1em' }}>Resultados do Processo #{process_id}</h2>
                {loading && <p>Carregando...</p>}
                {error && <div className="alert alert-danger">{error}</div>}
                {!loading && !error && (
                    results.length > 0 ? (
                        <ul className="list-group">
                            {results.map((result, idx) => (
                                <li className="list-group-item" key={idx}>
                                    <pre>{JSON.stringify(result, null, 2)}</pre>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <div className="alert alert-info mt-3">
                            Nenhum resultado disponível para este processo.
                        </div>
                    )
                )}
            </main>
        </div>
    );
};

export default ImageResults;