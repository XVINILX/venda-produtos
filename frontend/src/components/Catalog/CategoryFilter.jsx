// frontend/src/components/Catalog/CategoryFilter.jsx
import React from "react";
import "./CategoryFilter.css";

const CategoryFilter = ({ categories, selectedCategory, onCategoryChange }) => {
  return (
    <div className="category-filter">
      <h3 className="filter-title">Categorias</h3>
      <div className="category-buttons">
        <button
          className={`category-btn ${selectedCategory === "todos" ? "active" : ""}`}
          onClick={() => onCategoryChange("todos")}
        >
          Todos
        </button>
        {categories.map((category) => (
          <button
            key={category}
            className={`category-btn ${selectedCategory === category ? "active" : ""}`}
            onClick={() => onCategoryChange(category)}
          >
            {category}
          </button>
        ))}
      </div>
    </div>
  );
};

export default CategoryFilter;
