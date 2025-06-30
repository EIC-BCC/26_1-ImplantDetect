import { useSelector } from 'react-redux';

const Header = () => {

    const { user } = useSelector((state) => state.user);

    return (
        <>
            <header>
                <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
                    <div className="container-fluid">
                        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                            <span className="navbar-toggler-icon"></span>
                        </button>
                        <div id="navbarNav" className="collapse navbar-collapse justify-content-md-center">
                            <ul className="navbar-nav">
                                <li className="nav-item d-flex align-items-center">
                                    <i className="bi bi-box-arrow-in-down text-white" style={{ fontSize: '24px' }}></i>
                                    <a className="nav-link" href="/">ImplantDetect</a>
                                </li>
                                {user ? (
                                    <>
                                        <li className="nav-item">
                                            <a className="nav-link" href="/upload">Enviar</a>
                                        </li>
                                        <li className="nav-item dropdown">
                                            <button className="nav-link dropdown-toggle" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                                Olá, {user.username}!
                                            </button>
                                            <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
                                                <li><a className="dropdown-item" href="/logout">Sair</a></li>
                                            </ul>
                                        </li>
                                    </>
                                ) : (
                                    <>
                                        <li className="nav-item">
                                            <a className="nav-link" href="/login">Login</a>
                                        </li>
                                        <li className="nav-item">
                                            <a className="nav-link" href="/register">Register</a>
                                        </li>
                                    </>
                                )}
                            </ul>
                        </div>
                    </div>
                </nav>
            </header>
        </>
    );
}

export default Header;