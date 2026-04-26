import { useEffect, useState, useRef, Fragment } from "react";
import { useParams } from "react-router-dom";
import ImageService from "../../state/services/imageService";

// Paleta de cores para as bounding boxes
const COLORS = [
  "#00ff00",
  "#ff0000",
  "#0000ff",
  "#ffff00",
  "#ff00ff",
  "#00ffff",
];

// Função para obter cor baseada no índice
const getColor = (index) => COLORS[index % COLORS.length];

const ImageResults = () => {
  const { process_id } = useParams();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedRow, setExpandedRow] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [hoveredBox, setHoveredBox] = useState(null);
  const [visibleBoxes, setVisibleBoxes] = useState(new Set());
  const imageRef = useRef(null);

  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      setError("");
      try {
        const data = await ImageService.getProcessResults(process_id);
        setResults(data);
        if (data?.length > 0) {
          setImageUrl(`/api/uploads/${data[0].image_url}`);
        }
      } catch (err) {
        setError(
          "Erro ao buscar resultados do processo: " +
            (err.message || "Erro desconhecido"),
        );
        console.error("Error fetching process results:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [process_id]);

  // Inicializar visibleBoxes quando results mudar
  useEffect(() => {
    if (results.length > 0) {
      const isValidResult = (result) => {
        if (result.message) return false;
        if (result.class_name === "Classe None" || !result.class_name)
          return false;
        if (
          result.bb_x1_center == null ||
          result.bb_y1_center == null ||
          result.bb_x2_center == null ||
          result.bb_y2_center == null ||
          result.bb_x3_center == null ||
          result.bb_y3_center == null ||
          result.bb_x4_center == null ||
          result.bb_y4_center == null
        ) {
          return false;
        }
        return true;
      };
      const valid = results.filter(isValidResult);
      setVisibleBoxes(new Set(valid.map((_, idx) => idx)));
    }
  }, [results]);

  const toggleRow = (index) => {
    setExpandedRow(expandedRow === index ? null : index);
  };

  const toggleBoxVisibility = (index) => {
    setVisibleBoxes((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const handleImageLoad = () => {
    if (imageRef.current) {
      setVisibleBoxes((prev) => new Set(prev));
    }
  };

  if (loading)
    return (
      <div
        className="container"
        style={{ maxWidth: "48em", margin: "0 auto", padding: "3em 1em" }}
      >
        <p>Carregando...</p>
      </div>
    );
  if (error)
    return (
      <div
        className="container"
        style={{ maxWidth: "48em", margin: "0 auto", padding: "3em 1em" }}
      >
        <div className="alert alert-danger">{error}</div>
      </div>
    );

  const isValidResult = (result) => {
    if (result.message) return false;

    if (result.class_name === "Classe None" || !result.class_name) return false;

    if (
      result.bb_x1_center == null ||
      result.bb_y1_center == null ||
      result.bb_x2_center == null ||
      result.bb_y2_center == null ||
      result.bb_x3_center == null ||
      result.bb_y3_center == null ||
      result.bb_x4_center == null ||
      result.bb_y4_center == null
    ) {
      return false;
    }

    return true;
  };

  const validResults = results.filter(isValidResult);
  const hasErrors = results.length > 0 && validResults.length === 0;
  const errorMessage = results.find((r) => r.message)?.message;

  return (
    <div
      className="container"
      style={{ maxWidth: "64em", margin: "0 auto", padding: "2em 1em" }}
    >
      <main>
        <h2 className="text-center mb-4">
          Resultados do Processo #{process_id}
        </h2>

        {results.length === 0 ? (
          <div className="alert alert-info">
            Nenhum resultado disponível para este processo.
          </div>
        ) : hasErrors && validResults.length === 0 ? (
          <>
            {imageUrl && (
              <div className="mb-4" style={{ textAlign: "center" }}>
                <div
                  style={{
                    position: "relative",
                    display: "inline-block",
                    maxWidth: "100%",
                  }}
                >
                  <img
                    ref={imageRef}
                    src={imageUrl}
                    alt="Imagem processada"
                    onLoad={handleImageLoad}
                    style={{
                      width: "600px",
                      maxWidth: "100%",
                      height: "auto",
                      display: "block",
                      border: "1px solid #ddd",
                      borderRadius: "4px",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                    }}
                  />
                </div>
              </div>
            )}
            <div className="alert alert-warning">
              <h5 className="alert-heading">
                <i className="bi bi-exclamation-triangle-fill"></i> Nenhum
                implante detectado
              </h5>
              <p className="mb-0">
                {errorMessage ? (
                  <>Erro no processamento: {errorMessage}</>
                ) : (
                  "Não foram encontrados implantes na imagem processada."
                )}
              </p>
            </div>
          </>
        ) : (
          <>
            {imageUrl && (
              <div className="mb-4" style={{ textAlign: "center" }}>
                <div
                  style={{
                    position: "relative",
                    display: "inline-block",
                    maxWidth: "100%",
                  }}
                >
                  <img
                    ref={imageRef}
                    src={imageUrl}
                    alt="Imagem processada"
                    onLoad={handleImageLoad}
                    style={{
                      width: "600px",
                      maxWidth: "100%",
                      height: "auto",
                      display: "block",
                      border: "1px solid #ddd",
                      borderRadius: "4px",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                    }}
                  />

                  {validResults.map((result, idx) => {
                    if (!visibleBoxes.has(idx)) return null;

                    const color = getColor(idx);
                    const points = `${result.bb_x1_center},${result.bb_y1_center} ${result.bb_x2_center},${result.bb_y2_center} ${result.bb_x3_center},${result.bb_y3_center} ${result.bb_x4_center},${result.bb_y4_center}`;

                    return (
                      <svg
                        key={idx}
                        style={{
                          position: "absolute",
                          top: 0,
                          left: 0,
                          width: "100%",
                          height: "100%",
                          pointerEvents: "none",
                        }}
                        viewBox={`0 0 ${imageRef.current?.naturalWidth || 1} ${imageRef.current?.naturalHeight || 1}`}
                        preserveAspectRatio="none"
                      >
                        <polygon
                          points={points}
                          fill="none"
                          stroke={color}
                          strokeWidth="4"
                          opacity={hoveredBox === idx ? 1 : 0.7}
                          style={{ transition: "opacity 0.2s" }}
                        />
                        <text
                          x={result.bb_x1_center}
                          y={result.bb_y1_center - 10}
                          fill={color}
                          fontSize="24"
                          fontWeight="bold"
                          stroke="#000"
                          strokeWidth="1"
                          paintOrder="stroke"
                        >
                          {result.class_name} (
                          {(result.confidence * 100).toFixed(0)}%)
                        </text>
                      </svg>
                    );
                  })}
                </div>
              </div>
            )}

            <table className="table table-hover">
              <thead className="table-light">
                <tr>
                  <th style={{ width: "50px" }}>Visível</th>
                  <th>Classe Detectada</th>
                  <th>Confiança</th>
                  <th style={{ width: "100px" }}>Detalhes</th>
                </tr>
              </thead>
              <tbody>
                {validResults.map((result, idx) => (
                  <Fragment key={idx}>
                    <tr
                      onMouseEnter={() => setHoveredBox(idx)}
                      onMouseLeave={() => setHoveredBox(null)}
                      style={{
                        backgroundColor:
                          hoveredBox === idx
                            ? "rgba(0,123,255,0.08)"
                            : "transparent",
                        transition: "background-color 0.2s",
                      }}
                    >
                      <td className="text-center">
                        <input
                          type="checkbox"
                          checked={visibleBoxes.has(idx)}
                          onChange={() => toggleBoxVisibility(idx)}
                          style={{
                            cursor: "pointer",
                            width: "18px",
                            height: "18px",
                          }}
                        />
                      </td>
                      <td
                        onClick={() => toggleRow(idx)}
                        style={{ cursor: "pointer" }}
                      >
                        <span
                          style={{
                            display: "inline-block",
                            width: "14px",
                            height: "14px",
                            backgroundColor: getColor(idx),
                            marginRight: "10px",
                            border: "1px solid #000",
                            borderRadius: "2px",
                            verticalAlign: "middle",
                          }}
                        ></span>
                        <strong>{result.class_name}</strong>
                      </td>
                      <td
                        onClick={() => toggleRow(idx)}
                        style={{ cursor: "pointer" }}
                      >
                        {(result.confidence * 100).toFixed(1)}%
                      </td>
                      <td
                        className="text-center"
                        onClick={() => toggleRow(idx)}
                        style={{ cursor: "pointer" }}
                      >
                        <span className="badge bg-secondary">
                          {expandedRow === idx ? "▲ Ocultar" : "▼ Mostrar"}
                        </span>
                      </td>
                    </tr>
                    {expandedRow === idx && (
                      <tr>
                        <td
                          colSpan="4"
                          style={{ backgroundColor: "#f8f9fa", padding: "1em" }}
                        >
                          <strong>Coordenadas da Bounding Box:</strong>
                          <div
                            style={{
                              marginTop: "0.5em",
                              fontFamily: "monospace",
                            }}
                          >
                            <div>
                              Ponto 1: ({(result.bb_x1_center ?? 0).toFixed(2)},{" "}
                              {(result.bb_y1_center ?? 0).toFixed(2)})
                            </div>
                            <div>
                              Ponto 2: ({(result.bb_x2_center ?? 0).toFixed(2)},{" "}
                              {(result.bb_y2_center ?? 0).toFixed(2)})
                            </div>
                            <div>
                              Ponto 3: ({(result.bb_x3_center ?? 0).toFixed(2)},{" "}
                              {(result.bb_y3_center ?? 0).toFixed(2)})
                            </div>
                            <div>
                              Ponto 4: ({(result.bb_x4_center ?? 0).toFixed(2)},{" "}
                              {(result.bb_y4_center ?? 0).toFixed(2)})
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </>
        )}
      </main>
    </div>
  );
};

export default ImageResults;
