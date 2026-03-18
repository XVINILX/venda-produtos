// frontend/src/utils/dashboardUtils.js

/**
 * Formata valor para moeda brasileira
 * @param {number} value - Valor a ser formatado
 * @returns {string} Valor formatado (ex: R$ 1.234,56)
 */
export const formatCurrency = (value) => {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value || 0);
};

/**
 * Formata número com separadores brasileiros
 * @param {number} value - Valor a ser formatado
 * @returns {string} Número formatado (ex: 1.234)
 */
export const formatNumber = (value) => {
  return new Intl.NumberFormat("pt-BR").format(value || 0);
};

/**
 * Formata data para o formato brasileiro
 * @param {string} dateString - Data em string ISO
 * @returns {string} Data formatada (ex: 18/03/2026)
 */
export const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("pt-BR");
};

/**
 * Calcula percentual de crescimento
 * @param {number} current - Valor atual
 * @param {number} previous - Valor anterior
 * @returns {Object} Objeto com crescimento e sinal
 */
export const calculateGrowth = (current, previous) => {
  if (previous === 0) return { value: 100, isPositive: true };
  const growth = ((current - previous) / previous) * 100;
  return {
    value: Math.round(growth * 100) / 100,
    isPositive: growth >= 0,
  };
};

/**
 * Agrupa dados por categoria
 * @param {Array} data - Dados a serem agrupados
 * @param {string} categoryKey - Chave da categoria
 * @param {string} valueKey - Chave do valor a ser somado
 * @returns {Object} Dados agrupados
 */
export const groupByCategory = (data, categoryKey, valueKey) => {
  return data.reduce((acc, item) => {
    const category = item[categoryKey];
    if (!acc[category]) {
      acc[category] = {
        category,
        count: 0,
        total: 0,
        items: [],
      };
    }
    acc[category].count += 1;
    acc[category].total += item[valueKey] || 0;
    acc[category].items.push(item);
    return acc;
  }, {});
};

/**
 * Prepara dados para gráfico de pizza
 * @param {Array} data - Dados a serem plotados
 * @param {string} labelKey - Chave para rótulo
 * @param {string} valueKey - Chave para valor
 * @returns {Array} Dados formatados para gráfico
 */
export const preparePieChartData = (data, labelKey, valueKey) => {
  return data.map((item) => ({
    label: item[labelKey],
    value: item[valueKey] || 0,
  }));
};

/**
 * Prepara dados para gráfico de barras
 * @param {Array} data - Dados a serem plotados
 * @param {string} xKey - Chave para eixo X
 * @param {string} yKey - Chave para eixo Y
 * @returns {Array} Dados formatados para gráfico
 */
export const prepareBarChartData = (data, xKey, yKey) => {
  return data.map((item) => ({
    x: item[xKey],
    y: item[yKey] || 0,
  }));
};

/**
 * Calcula totais do dashboard
 * @param {Object} stats - Estatísticas do dashboard
 * @returns {Object} Totais calculados
 */
export const calculateTotals = (stats) => {
  return {
    totalProducts: stats?.total_products || 0,
    totalCategories: stats?.total_categories || 0,
    totalUsers: stats?.total_users || 0,
    totalOrders: stats?.total_orders || 0,
    totalRevenue: stats?.total_revenue || 0,
    averageOrderValue: stats?.average_order_value || 0,
    lowStockCount: stats?.products_low_stock || 0,
    outOfStockCount: stats?.products_out_of_stock || 0,
  };
};

/**
 * Filtra produtos por status de estoque
 * @param {Array} products - Lista de produtos
 * @param {string} status - Status ('all', 'low', 'out', 'normal')
 * @returns {Array} Produtos filtrados
 */
export const filterProductsByStock = (products, status) => {
  switch (status) {
    case "low":
      return products.filter((p) => p.stock > 0 && p.stock <= 5);
    case "out":
      return products.filter((p) => p.stock === 0);
    case "normal":
      return products.filter((p) => p.stock > 5);
    default:
      return products;
  }
};

/**
 * Ordena produtos por diferentes critérios
 * @param {Array} products - Lista de produtos
 * @param {string} sortBy - Critério ('name', 'price', 'stock', 'revenue')
 * @param {string} order - Ordem ('asc' ou 'desc')
 * @returns {Array} Produtos ordenados
 */
export const sortProducts = (products, sortBy = "name", order = "asc") => {
  const sorted = [...products].sort((a, b) => {
    let comparison = 0;

    switch (sortBy) {
      case "name":
        comparison = a.name.localeCompare(b.name);
        break;
      case "price":
        comparison = a.price - b.price;
        break;
      case "stock":
        comparison = a.stock - b.stock;
        break;
      case "revenue":
        comparison = (a.revenue || 0) - (b.revenue || 0);
        break;
      default:
        comparison = 0;
    }

    return order === "asc" ? comparison : -comparison;
  });

  return sorted;
};

// Exportar todos os utilitários
const dashboardUtils = {
  formatCurrency,
  formatNumber,
  formatDate,
  calculateGrowth,
  groupByCategory,
  preparePieChartData,
  prepareBarChartData,
  calculateTotals,
  filterProductsByStock,
  sortProducts,
};

export default dashboardUtils;
