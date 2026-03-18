// frontend/src/services/adminService.js
import api from "./api";

// ==================== DASHBOARD ====================

/**
 * Busca estatísticas gerais do dashboard
 * @returns {Promise<Object>} Estatísticas do dashboard
 */
export const getDashboardStats = async () => {
  try {
    const response = await api.get("/admin/dashboard");
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar estatísticas do dashboard:", error);
    throw error;
  }
};

// ==================== PRODUTOS ====================

/**
 * Busca todos os produtos com dados de venda
 * @returns {Promise<Array>} Lista de produtos com informações de vendas
 */
export const getProductsWithSales = async () => {
  try {
    const response = await api.get("/admin/products");
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar produtos com vendas:", error);
    throw error;
  }
};

/**
 * Busca produtos com estoque baixo
 * @param {number} threshold - Limite de estoque baixo (padrão: 5)
 * @returns {Promise<Array>} Lista de produtos com estoque baixo
 */
export const getLowStockProducts = async (threshold = 5) => {
  try {
    const response = await api.get(
      `/admin/products/low-stock?threshold=${threshold}`,
    );
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar produtos com estoque baixo:", error);
    throw error;
  }
};

/**
 * Busca os produtos mais vendidos
 * @param {number} limit - Número de produtos a retornar (padrão: 5)
 * @returns {Promise<Array>} Lista dos produtos mais vendidos
 */
export const getTopSellingProducts = async (limit = 5) => {
  try {
    const response = await api.get(
      `/admin/products/top-selling?limit=${limit}`,
    );
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar produtos mais vendidos:", error);
    throw error;
  }
};

/**
 * Atualiza o estoque de um produto
 * @param {number} productId - ID do produto
 * @param {number} newStock - Novo valor de estoque
 * @returns {Promise<Object>} Produto atualizado
 */
export const updateProductStock = async (productId, newStock) => {
  try {
    const response = await api.patch(
      `/admin/products/${productId}/stock?new_stock=${newStock}`,
    );
    return response.data;
  } catch (error) {
    console.error("Erro ao atualizar estoque:", error);
    throw error;
  }
};

// ==================== VENDAS ====================

/**
 * Busca vendas diárias
 * @param {number} days - Número de dias para buscar (padrão: 7)
 * @returns {Promise<Array>} Lista de vendas diárias
 */
export const getDailySales = async (days = 7) => {
  try {
    const response = await api.get(`/admin/sales/daily?days=${days}`);
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar vendas diárias:", error);
    throw error;
  }
};

/**
 * Busca vendas agrupadas por categoria
 * @returns {Promise<Array>} Lista de vendas por categoria
 */
export const getSalesByCategory = async () => {
  try {
    const response = await api.get("/admin/sales/by-category");
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar vendas por categoria:", error);
    throw error;
  }
};

// ==================== USUÁRIOS ====================

/**
 * Busca todos os usuários
 * @returns {Promise<Array>} Lista de usuários
 */
export const getAllUsers = async () => {
  try {
    const response = await api.get("/admin/users");
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar usuários:", error);
    throw error;
  }
};

// ==================== EXPORTAÇÃO DE DADOS ====================

/**
 * Exporta dados em formato CSV
 * @param {Array} data - Dados a serem exportados
 * @param {string} filename - Nome do arquivo
 */
export const exportToCSV = (data, filename) => {
  if (!data || data.length === 0) {
    console.warn("Sem dados para exportar");
    return;
  }

  // Pegar cabeçalhos do primeiro objeto
  const headers = Object.keys(data[0]);

  // Criar linhas CSV
  const csvRows = [];
  csvRows.push(headers.join(","));

  for (const row of data) {
    const values = headers.map((header) => {
      const value = row[header]?.toString() || "";
      // Escapar vírgulas e aspas
      return value.includes(",") ? `"${value}"` : value;
    });
    csvRows.push(values.join(","));
  }

  const csvString = csvRows.join("\n");

  // Criar e baixar arquivo
  const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}.csv`);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Exporta dados em formato JSON
 * @param {Array} data - Dados a serem exportados
 * @param {string} filename - Nome do arquivo
 */
export const exportToJSON = (data, filename) => {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: "application/json" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `${filename}.json`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// ==================== RELATÓRIOS ====================

/**
 * Gera relatório de vendas por período
 * @param {string} startDate - Data inicial (YYYY-MM-DD)
 * @param {string} endDate - Data final (YYYY-MM-DD)
 * @returns {Promise<Object>} Relatório de vendas
 */
export const getSalesReport = async (startDate, endDate) => {
  try {
    const response = await api.get(
      `/admin/reports/sales?start=${startDate}&end=${endDate}`,
    );
    return response.data;
  } catch (error) {
    console.error("Erro ao gerar relatório de vendas:", error);
    throw error;
  }
};

/**
 * Gera relatório de estoque
 * @returns {Promise<Object>} Relatório de estoque
 */
export const getStockReport = async () => {
  try {
    const response = await api.get("/admin/reports/stock");
    return response.data;
  } catch (error) {
    console.error("Erro ao gerar relatório de estoque:", error);
    throw error;
  }
};

// ==================== MÉTRICAS ====================

/**
 * Calcula métricas de crescimento
 * @param {Array} salesData - Dados de vendas
 * @returns {Object} Métricas de crescimento
 */
export const calculateGrowthMetrics = (salesData) => {
  if (!salesData || salesData.length < 2) {
    return {
      revenueGrowth: 0,
      ordersGrowth: 0,
      averageTicketGrowth: 0,
    };
  }

  const lastPeriod = salesData.slice(-2);
  const current = lastPeriod[1];
  const previous = lastPeriod[0];

  const revenueGrowth =
    ((current.revenue - previous.revenue) / previous.revenue) * 100;
  const ordersGrowth =
    ((current.orders - previous.orders) / previous.orders) * 100;

  const currentAvgTicket = current.revenue / current.orders;
  const previousAvgTicket = previous.revenue / previous.orders;
  const averageTicketGrowth =
    ((currentAvgTicket - previousAvgTicket) / previousAvgTicket) * 100;

  return {
    revenueGrowth: Math.round(revenueGrowth * 100) / 100,
    ordersGrowth: Math.round(ordersGrowth * 100) / 100,
    averageTicketGrowth: Math.round(averageTicketGrowth * 100) / 100,
  };
};

// Exportar tudo como um objeto também
const adminService = {
  getDashboardStats,
  getProductsWithSales,
  getLowStockProducts,
  getTopSellingProducts,
  updateProductStock,
  getDailySales,
  getSalesByCategory,
  getAllUsers,
  exportToCSV,
  exportToJSON,
  getSalesReport,
  getStockReport,
  calculateGrowthMetrics,
};

export default adminService;
