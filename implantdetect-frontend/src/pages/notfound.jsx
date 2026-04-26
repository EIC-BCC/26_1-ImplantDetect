const NotFound = () => {
  return (
    <div
      className="d-flex w-100 h-100 p-3 mx-auto flex-column align-items-center text-center"
      style={{ maxWidth: "42em" }}
    >
      <main className="px-3">
        <h1>Erro 404</h1>
        <p className="lead">
          Não foi possível encontrar a página que você está procurando.
        </p>
      </main>
    </div>
  );
};

export default NotFound;
