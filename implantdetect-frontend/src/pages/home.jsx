const Home = () => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "60vh",
      }}
    >
      <h1
        style={{
          marginBottom: "10px",
          fontSize: "3em",
          display: "flex",
          alignItems: "center",
        }}
      >
        <span>ImplantDetect</span>
        <span style={{ fontSize: "1.2em", marginLeft: "0.5em" }}>🦷🔍</span>
      </h1>
      <p style={{ maxWidth: "600px", textAlign: "center" }}>
        O ImplantDetect é uma plataforma desenvolvida para auxiliar na detecção
        de implantes dentários em imagens radiográficas utilizando técnicas de
        aprendizado de máquina.
      </p>
      <p style={{ fontSize: "0.9em", color: "#888", marginTop: "30px" }}>
        Projeto e Construção de Sistemas 2025.1 — Código fonte disponível no{" "}
        <a
          href="https://github.com/marceloareas/implantdetect"
          target="_blank"
          rel="noopener noreferrer"
        >
          GitHub
        </a>
      </p>
    </div>
  );
};

export default Home;
