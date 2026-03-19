// frontend/src/components/admin/EditProductModal.jsx
import React, { useState, useEffect } from "react";
import { X, Save, Image } from "lucide-react";
import "./CreateProductModal.css"; // Reutilizar o mesmo CSS

const EditProductModal = ({ isOpen, onClose, onEdit, product }) => {
  const [formData, setFormData] = useState({
    name: "",
    price: "",
    category: "",
    stock: "",
    image_url: "",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  // Carregar dados do produto quando o modal abrir
  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || "",
        price: product.price || "",
        category: product.category || "",
        stock: product.stock || "",
        image_url: product.image_url || "",
      });
    }
  }, [product]);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) newErrors.name = "Nome é obrigatório";
    if (formData.price && formData.price <= 0) {
      newErrors.price = "Preço deve ser maior que zero";
    }
    if (formData.stock && formData.stock < 0) {
      newErrors.stock = "Estoque não pode ser negativo";
    }

    return newErrors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Limpar erro do campo quando começar a digitar
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    try {
      // Preparar dados para envio (apenas campos modificados)
      const updateData = {};

      if (formData.name !== product.name)
        updateData.name = formData.name.trim();

      if (parseFloat(formData.price) !== product.price) {
        updateData.price = parseFloat(formData.price);
      }
      if (formData.category !== product.category) {
        updateData.category = formData.category;
      }
      if (parseInt(formData.stock) !== product.stock) {
        updateData.stock = parseInt(formData.stock);
      }
      if (formData.image_url !== product.image_url) {
        updateData.image_url = formData.image_url?.trim() || null;
      }

      await onEdit(product.id, updateData);
      onClose();
    } catch (error) {
      console.error("Erro ao editar produto:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content create-product-modal">
        <div className="modal-header">
          <h2>Editar Produto</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Nome do Produto *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className={errors.name ? "error" : ""}
              placeholder="Ex: Notebook Gamer"
            />
            {errors.name && (
              <span className="error-message">{errors.name}</span>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="price">Preço (R$)</label>
              <input
                type="number"
                id="price"
                name="price"
                value={formData.price}
                onChange={handleChange}
                className={errors.price ? "error" : ""}
                placeholder="0.00"
                step="0.01"
                min="0"
              />
              {errors.price && (
                <span className="error-message">{errors.price}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="stock">Estoque</label>
              <input
                type="number"
                id="stock"
                name="stock"
                value={formData.stock}
                onChange={handleChange}
                className={errors.stock ? "error" : ""}
                placeholder="0"
                min="0"
              />
              {errors.stock && (
                <span className="error-message">{errors.stock}</span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="category">Categoria</label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className={errors.category ? "error" : ""}
            >
              <option value="">Selecione uma categoria</option>
              <option value="eletrônicos">Eletrônicos</option>
              <option value="roupas">Roupas</option>
              <option value="calçados">Calçados</option>
              <option value="acessórios">Acessórios</option>
              <option value="livros">Livros</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="image_url">URL da Imagem</label>
            <div className="image-input-wrapper">
              <Image size={20} />
              <input
                type="url"
                id="image_url"
                name="image_url"
                value={formData.image_url}
                onChange={handleChange}
                placeholder="https://exemplo.com/imagem.jpg"
              />
            </div>
          </div>

          {formData.image_url && (
            <div className="image-preview">
              <img
                src={formData.image_url}
                alt="Preview"
                onError={(e) => {
                  e.target.src =
                    "https://via.placeholder.com/200?text=Imagem+invalida";
                }}
              />
            </div>
          )}

          <div className="modal-actions">
            <button type="button" className="cancel-btn" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="save-btn" disabled={loading}>
              {loading ? (
                <>
                  <div className="loading-spinner-small"></div>
                  Salvando...
                </>
              ) : (
                <>
                  <Save size={18} />
                  Salvar Alterações
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditProductModal;
