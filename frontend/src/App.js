import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainApp from "./components/HomePage";
import PanelApp from "./components/PanelApp";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainApp />} />
          <Route path="/panel/*" element={<PanelApp />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;