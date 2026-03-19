import api from "./api";

export const getProducts = async (category = null) => {
  const url = category
    ? `/products?category=${encodeURIComponent(category)}`
    : "/products/";
  const response = await api.get(url);
  return response.data;
};

export const getProduct = async (id) => {
  const response = await api.get(`/products/${id}`);
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get("/products/categories/");
  return response.data.categories;
};

export const searchProducts = async (term) => {
  const response = await api.get(
    `/products/search?q=${encodeURIComponent(term)}`,
  );
  return response.data;
};

export const checkStock = async (productId, quantity) => {
  const response = await api.get(
    `/products/${productId}/stock?quantity=${quantity}`,
  );
  return response.data;
};

export const getLowStockProducts = async (threshold = 5) => {
  const response = await api.get(`/products/low-stock?threshold=${threshold}`);
  return response.data;
};

/**
 * Atualiza um produto existente (requer admin)
 * @param {number} id - ID do produto
 * @param {Object} productData - Dados a serem atualizados
 * @param {string} productData.name - Nome do produto (opcional)
 * @param {number} productData.price - Preço do produto (opcional)
 * @param {string} productData.category - Categoria do produto (opcional)
 * @param {number} productData.stock - Quantidade em estoque (opcional)
 * @param {string} productData.image_url - URL da imagem (opcional)
 * @returns {Promise<Object>} Produto atualizado
 */
export const updateProduct = async (id, productData) => {
  try {
    // Filtrar apenas campos que foram enviados
    const updateData = {};

    if (productData.name !== undefined) {
      if (productData.name.trim() === "") {
        throw new Error("Nome não pode ser vazio");
      }
      updateData.name = productData.name.trim();
    }

    if (productData.price !== undefined) {
      if (productData.price <= 0) {
        throw new Error("Preço deve ser maior que zero");
      }
      updateData.price = parseFloat(productData.price);
    }

    if (productData.category !== undefined) {
      if (!productData.category) {
        throw new Error("Categoria não pode ser vazia");
      }
      updateData.category = productData.category.toLowerCase().trim();
    }

    if (productData.stock !== undefined) {
      if (productData.stock < 0) {
        throw new Error("Estoque não pode ser negativo");
      }
      updateData.stock = parseInt(productData.stock);
    }

    if (productData.image_url !== undefined) {
      updateData.image_url = productData.image_url?.trim() || null;
    }

    const response = await api.patch(`/products/${id}`, updateData);
    return response.data;
  } catch (error) {
    console.error(`Erro ao atualizar produto ${id}:`, error);
    throw error;
  }
};

// ==================== DELETE (Admin apenas) ====================

/**
 * Remove um produto (requer admin)
 * @param {number} id - ID do produto
 * @returns {Promise<void>}
 */
export const deleteProduct = async (id) => {
  try {
    await api.delete(`/products/${id}`);
  } catch (error) {
    console.error(`Erro ao remover produto ${id}:`, error);
    throw error;
  }
};

/**
 * Cria um novo produto (requer admin)
 * @param {Object} productData - Dados do produto
 * @param {string} productData.name - Nome do produto
 * @param {number} productData.price - Preço do produto
 * @param {string} productData.category - Categoria do produto
 * @param {number} productData.stock - Quantidade em estoque
 * @param {string} productData.image_url - URL da imagem (opcional)
 * @returns {Promise<Object>} Produto criado
 */
export const createProduct = async (productData) => {
  try {
    // Validação básica no frontend
    if (!productData.name || productData.name.trim() === "") {
      throw new Error("Nome do produto é obrigatório");
    }
    if (!productData.price || productData.price <= 0) {
      throw new Error("Preço deve ser maior que zero");
    }
    if (!productData.category) {
      throw new Error("Categoria é obrigatória");
    }
    if (productData.stock === undefined || productData.stock < 0) {
      throw new Error("Estoque não pode ser negativo");
    }

    const response = await api.post("/products/", {
      name: productData.name.trim(),
      price: parseFloat(productData.price),
      category: productData.category.toLowerCase().trim(),
      stock: parseInt(productData.stock) || 0,
      image_url: productData.image_url?.trim() || null,
    });

    return response.data;
  } catch (error) {
    console.error("Erro ao criar produto:", error);
    throw error;
  }
};
