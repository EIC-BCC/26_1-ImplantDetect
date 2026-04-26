import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useSelector } from "react-redux";

import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/css/bootstrap.min.css";

// Components
import Header from "./components/header";

// Pages
import ImageUpload from "./pages/images/upload";
import ImageResults from "./pages/images/results";
import Unauthorized from "./pages/unauthorized";
import NotFound from "./pages/notfound";
import Register from "./pages/register";
import Logout from "./pages/logout";
import Login from "./pages/login";
import Home from "./pages/home";

function AuthenticatedRoute({ children }) {
  const isAuthenticated = useSelector((state) => state.user.user !== null);

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return children;
}

function App() {
  return (
    <BrowserRouter>
      <div
        style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}
      >
        <Header />
        <div className="container mt-5 flex-fill">
          <Routes>
            <Route path="/" element={<Navigate to="/login" />} />

            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/logout" element={<Logout />} />
            <Route
              path="/process/:process_id/results"
              element={<ImageResults />}
            />
            <Route
              path="/home"
              element={
                <AuthenticatedRoute>
                  <Home />
                </AuthenticatedRoute>
              }
            />
            <Route
              path="/images/upload"
              element={
                <AuthenticatedRoute>
                  <ImageUpload />
                </AuthenticatedRoute>
              }
            />

            <Route path="/403" element={<Unauthorized />} />
            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<Navigate to="/404" />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
