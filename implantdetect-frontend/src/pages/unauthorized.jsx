const Unauthorized = () => {
  return (
    <div
      className="d-flex w-100 h-100 p-3 mx-auto flex-column align-items-center text-center"
      style={{ maxWidth: "42em" }}
    >
      <main className="px-3">
        <h1>Erro 403</h1>
        <p className="lead">Você não tem permissão para acessar esta página.</p>
      </main>
    </div>
  );
};

export default Unauthorized;
