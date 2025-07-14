import { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const QRGenerator = () => {
  const [text, setText] = useState("");
  const [size, setSize] = useState(10);
  const [border, setBorder] = useState(4);
  const [qrCode, setQrCode] = useState(null);
  const [qrCodes, setQrCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generateQR = async () => {
    if (!text.trim()) {
      setError("Proszę wprowadź tekst do kodu QR");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(`${API}/qr/generate`, {
        text: text,
        size: size,
        border: border
      });
      
      setQrCode(response.data);
      loadQRCodes(); // Refresh the list
    } catch (err) {
      setError("Błąd podczas generowania kodu QR: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const downloadQR = async (qrId) => {
    try {
      const response = await axios.get(`${API}/qr/download/${qrId}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `qr_code_${qrId}.jpg`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError("Błąd podczas pobierania kodu QR: " + (err.response?.data?.detail || err.message));
    }
  };

  const loadQRCodes = async () => {
    try {
      const response = await axios.get(`${API}/qr/list`);
      setQrCodes(response.data);
    } catch (err) {
      console.error("Błąd podczas ładowania kodów QR:", err);
    }
  };

  useEffect(() => {
    loadQRCodes();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Generator kodów QR
        </h1>

        {/* Generator form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Stwórz nowy kod QR</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tekst do kodu QR:
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              placeholder="Wprowadź tekst, URL, lub dane..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rozmiar (1-40):
              </label>
              <input
                type="number"
                value={size}
                onChange={(e) => setSize(parseInt(e.target.value) || 10)}
                min="1"
                max="40"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ramka (1-10):
              </label>
              <input
                type="number"
                value={border}
                onChange={(e) => setBorder(parseInt(e.target.value) || 4)}
                min="1"
                max="10"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <button
            onClick={generateQR}
            disabled={loading}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? "Generowanie..." : "Generuj kod QR"}
          </button>

          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Current QR Code */}
        {qrCode && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Wygenerowany kod QR</h2>
            <div className="text-center">
              <img
                src={`data:image/png;base64,${qrCode.image_base64}`}
                alt="Generated QR Code"
                className="mx-auto mb-4 border border-gray-300 rounded"
              />
              <p className="text-gray-600 mb-4">Tekst: {qrCode.text}</p>
              <button
                onClick={() => downloadQR(qrCode.id)}
                className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600"
              >
                Pobierz jako JPEG
              </button>
            </div>
          </div>
        )}

        {/* QR Codes List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Wszystkie kody QR</h2>
          {qrCodes.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Brak kodów QR</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {qrCodes.map((qr) => (
                <div key={qr.id} className="border border-gray-200 rounded-lg p-4">
                  <img
                    src={`data:image/png;base64,${qr.image_base64}`}
                    alt="QR Code"
                    className="w-full h-32 object-contain mb-2"
                  />
                  <p className="text-sm text-gray-600 mb-2 truncate" title={qr.text}>
                    {qr.text}
                  </p>
                  <p className="text-xs text-gray-400 mb-2">
                    {new Date(qr.timestamp).toLocaleString()}
                  </p>
                  <button
                    onClick={() => downloadQR(qr.id)}
                    className="w-full bg-blue-500 text-white py-1 px-2 rounded text-sm hover:bg-blue-600"
                  >
                    Pobierz JPEG
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const Home = () => {
  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data.message);
    } catch (e) {
      console.error(e, `errored out requesting / api`);
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return (
    <div>
      <header className="App-header">
        <a
          className="App-link"
          href="https://emergent.sh"
          target="_blank"
          rel="noopener noreferrer"
        >
          <img src="https://avatars.githubusercontent.com/in/1201222?s=120&u=2686cf91179bbafbc7a71bfbc43004cf9ae1acea&v=4" alt="Emergent" />
        </a>
        <p className="mt-5">Generator kodów QR ~!</p>
        <div className="mt-8">
          <a
            href="/qr"
            className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 text-decoration-none"
          >
            Przejdź do generatora QR
          </a>
        </div>
      </header>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/qr" element={<QRGenerator />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
