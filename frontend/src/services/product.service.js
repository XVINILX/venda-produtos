import api from "./api";

export const getProducts = async (category = null) => {
  const url = category
    ? `/products?category=${encodeURIComponent(category)}`
    : "/products";
  const response = await api.get(url);
  return response.data;
};

export const getProduct = async (id) => {
  const response = await api.get(`/products/${id}`);
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get("/products/categories");
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
