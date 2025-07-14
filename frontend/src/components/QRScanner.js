import React, { useState, useEffect, useRef } from 'react';

function QRScanner({ onScan, loading, disabled }) {
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);
  const [facingMode, setFacingMode] = useState('environment');
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    return () => {
      stopScanning();
    };
  }, []);

  const startScanning = async () => {
    try {
      setError(null);
      setIsScanning(true);

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }
    } catch (err) {
      setError('Nie można uzyskać dostępu do kamery');
      setIsScanning(false);
    }
  };

  const stopScanning = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsScanning(false);
  };

  const toggleCamera = () => {
    stopScanning();
    setFacingMode(facingMode === 'environment' ? 'user' : 'environment');
  };

  const handleVideoClick = () => {
    // Simulate QR code scanning for demo
    if (isScanning && !loading) {
      // Generate a mock QR code for demo
      const mockQRCodes = ['QR-EMP-001', 'QR-EMP-002', 'QR-INVALID-001'];
      const randomQR = mockQRCodes[Math.floor(Math.random() * mockQRCodes.length)];
      onScan(randomQR);
    }
  };

  useEffect(() => {
    if (isScanning && facingMode) {
      startScanning();
    }
  }, [facingMode]);

  return (
    <div className="qr-scanner-container">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="relative">
        {isScanning ? (
          <div className="relative">
            <video
              ref={videoRef}
              className="qr-scanner-video w-full h-64 object-cover rounded-lg"
              autoPlay
              playsInline
              onClick={handleVideoClick}
            />
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-48 h-48 border-2 border-white rounded-lg shadow-lg">
                <div className="w-full h-full border-2 border-dashed border-white/50 rounded-lg flex items-center justify-center">
                  <span className="text-white text-sm font-medium bg-black/50 px-2 py-1 rounded">
                    Kliknij aby zeskanować
                  </span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="w-full h-64 bg-gray-200 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Kamera nie jest aktywna</p>
          </div>
        )}

        {loading && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-lg">
            <div className="spinner"></div>
          </div>
        )}
      </div>

      <div className="flex gap-2 mt-4">
        <button
          onClick={isScanning ? stopScanning : startScanning}
          disabled={disabled}
          className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors ${
            isScanning
              ? 'bg-red-600 text-white hover:bg-red-700'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isScanning ? 'Zatrzymaj' : 'Uruchom skaner'}
        </button>

        {isScanning && (
          <button
            onClick={toggleCamera}
            disabled={disabled}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            📷
          </button>
        )}
      </div>

      <div className="mt-2 text-sm text-gray-600">
        <p>• Kamera: {facingMode === 'environment' ? 'Tylna' : 'Przednia'}</p>
        <p>• Kliknij na obraz aby zeskanować kod QR (demo)</p>
      </div>
    </div>
  );
}

export default QRScanner;