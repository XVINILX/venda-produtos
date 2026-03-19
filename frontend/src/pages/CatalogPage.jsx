// frontend/src/pages/CatalogPage.jsx
import React, { useState, useEffect } from "react";
import ProductCard from "../components/Catalog/ProductCard";
import CategoryFilter from "../components/Catalog/CategoryFilter";
import { getProducts, getCategories } from "../services/product.service";
import { Package } from "lucide-react";
import "./CatalogPage.css";

const CatalogPage = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("todos");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, [selectedCategory]);

  const fetchCategories = async () => {
    try {
      const data = await getCategories();
      setCategories(data);
    } catch (err) {
      console.error("Erro ao carregar categorias", err);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const category = selectedCategory === "todos" ? null : selectedCategory;
      const data = await getProducts(category);

      setProducts(data);
    } catch (err) {
      setError("Erro ao carregar produtos");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner-large"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-message">{error}</p>
        <button onClick={fetchProducts} className="retry-btn">
          Tentar novamente
        </button>
      </div>
    );
  }

  return (
    <div className="container catalog-page">
      <h1 className="page-title">Catálogo de Produtos</h1>

      <CategoryFilter
        categories={categories}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
      />

      {products.length === 0 ? (
        <div className="empty-state">
          <Package />
          <p>Nenhum produto encontrado</p>
        </div>
      ) : (
        <div className="products-grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
};

export default CatalogPage;
