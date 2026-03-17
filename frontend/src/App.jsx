// frontend/src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { CartProvider } from "./contexts/CartContext";
import Navbar from "./components/Layout/Navbar";
import CatalogPage from "./pages/CatalogPage";
import CartPage from "./pages/CartPage";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <CartProvider>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<CatalogPage />} />
              <Route path="/cart" element={<CartPage />} />
            </Routes>
          </main>
          <footer className="footer">
            <div className="container">
              <p>© 2024 Wise Sales - Mini E-commerce</p>
            </div>
          </footer>
        </div>
      </CartProvider>
    </BrowserRouter>
  );
}

export default App;
