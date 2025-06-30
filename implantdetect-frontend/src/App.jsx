import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from "react-redux";

import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/css/bootstrap.min.css";

// Components
import Header from './components/header';

// Pages
import ImageUpload from './pages/images/upload';

import Unauthorized from './pages/unauthorized';
import NotFound from './pages/notfound';
import Register from './pages/register';
import Logout from './pages/logout';
import Login from './pages/login';
import Home from './pages/home';

function AuthenticatedRoute({ children }) {
  const isAuthenticated = useSelector((state) => state.user.user !== null);

  if (!isAuthenticated) {
    return <Navigate to="/" />;
  }

  return children;
}

function App() {
  return (
    <>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <div className="container mt-5 flex-fill">
          <BrowserRouter>
            <Routes>
              {/* Open routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/logout" element={<Logout />} />
              <Route path="/register" element={<Register />} />

              {/* Catch-all route for 404 and 403 errors */}
              <Route path="*" element={<Navigate to="/404" />} />
              <Route path="/404" element={<NotFound />} />
              <Route path="/403" element={<Unauthorized />} />

              {/* Authenticated routes */}
              <Route path="/images/upload" element={<ImageUpload />} />np
              <Route element={<AuthenticatedRoute />}>
              </Route>
            </Routes>
          </BrowserRouter>
        </div>
      </div>
    </>
  );
}

export default App
