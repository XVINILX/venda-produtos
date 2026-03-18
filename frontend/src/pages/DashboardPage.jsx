// frontend/src/pages/admin/DashboardPage.jsx
import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import {
  BarChart3,
  Package,
  Users,
  ShoppingBag,
  DollarSign,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Layers,
  Calendar,
  ArrowUp,
  ArrowDown,
  Edit,
  Save,
  X,
} from "lucide-react";
import {
  getDashboardStats,
  getProductsWithSales,
  getDailySales,
  getSalesByCategory,
  getTopSellingProducts,
  getLowStockProducts,
  getAllUsers,
  updateProductStock,
  exportToCSV,
} from "../services/dashboard.service";
import {
  formatCurrency,
  formatNumber,
  calculateGrowth,
} from "../utils/dashboard_utils";
import "./DashboardPage.css";

const DashboardPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [salesByCategory, setSalesByCategory] = useState([]);
  const [dailySales, setDailySales] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [lowStockProducts, setLowStockProducts] = useState([]);
  const [users, setUsers] = useState([]);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [editingStock, setEditingStock] = useState(null);
  const [newStockValue, setNewStockValue] = useState(0);
  const [dateRange, setDateRange] = useState(7);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Carregar todos os dados em paralelo
        const [
          stats,
          products,
          dailySales,
          categorySales,
          topProducts,
          lowStock,
          users,
        ] = await Promise.all([
          getDashboardStats(),
          getProductsWithSales(),
          getDailySales(7),
          getSalesByCategory(),
          getTopSellingProducts(5),
          getLowStockProducts(5),
          getAllUsers(),
        ]);

        setStats(stats);
        setProducts(products);
        setDailySales(dailySales);
        setSalesByCategory(categorySales);
        setTopProducts(topProducts);
        setLowStockProducts(lowStock);
        setUsers(users);

        // Calcular crescimento
        if (dailySales.length >= 2) {
          const growth = calculateGrowth(
            dailySales[dailySales.length - 1].revenue,
            dailySales[dailySales.length - 2].revenue,
          );
          setRevenueGrowth(growth);
        }
      } catch (error) {
        console.error("Erro ao carregar dados:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Função para exportar dados
  const handleExportProducts = () => {
    exportToCSV(products, "produtos_exportados");
  };
  const handleStockUpdate = async (productId, newStock) => {
    try {
      await updateProductStock(productId, newStock);
      // Recarregar dados
      const updatedProducts = await getProductsWithSales();
      setProducts(updatedProducts);
      setEditingStock(null);
    } catch (error) {
      console.error("Erro ao atualizar estoque:", error);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat("pt-BR").format(value);
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="loading-spinner-large"></div>
        <p>Carregando dashboard...</p>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>
          <BarChart3 size={28} />
          Dashboard Administrativo
        </h1>
        <div className="admin-welcome">
          <span>Bem-vindo, {user?.name}</span>
          <span className="admin-badge">Administrador</span>
        </div>
      </div>

      <div className="admin-tabs">
        <button
          className={`tab-btn ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => setActiveTab("dashboard")}
        >
          <BarChart3 size={18} />
          Dashboard
        </button>
        <button
          className={`tab-btn ${activeTab === "products" ? "active" : ""}`}
          onClick={() => setActiveTab("products")}
        >
          <Package size={18} />
          Produtos
        </button>
        <button
          className={`tab-btn ${activeTab === "users" ? "active" : ""}`}
          onClick={() => setActiveTab("users")}
        >
          <Users size={18} />
          Usuários
        </button>
        <button
          className={`tab-btn ${activeTab === "reports" ? "active" : ""}`}
          onClick={() => setActiveTab("reports")}
        >
          <ShoppingBag size={18} />
          Relatórios
        </button>
      </div>

      <div className="admin-content">
        {activeTab === "dashboard" && (
          <>
            {/* Cards de Estatísticas */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon products">
                  <Package size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-label">Total de Produtos</span>
                  <span className="stat-value">
                    {formatNumber(stats?.total_products)}
                  </span>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon categories">
                  <Layers size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-label">Categorias</span>
                  <span className="stat-value">
                    {formatNumber(stats?.total_categories)}
                  </span>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon users">
                  <Users size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-label">Usuários</span>
                  <span className="stat-value">
                    {formatNumber(stats?.total_users)}
                  </span>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon orders">
                  <ShoppingBag size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-label">Pedidos</span>
                  <span className="stat-value">
                    {formatNumber(stats?.total_orders)}
                  </span>
                </div>
              </div>

              <div className="stat-card highlight">
                <div className="stat-icon revenue">
                  <DollarSign size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-label">Receita Total</span>
                  <span className="stat-value">
                    {formatCurrency(stats?.total_revenue)}
                  </span>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon avg">
                  <TrendingUp size={24} />
                </div>
                <div className="stat-info">
                  <span className="stat-label">Ticket Médio</span>
                  <span className="stat-value">
                    {formatCurrency(stats?.average_order_value)}
                  </span>
                </div>
              </div>
            </div>

            {/* Alertas de Estoque */}
            {(stats?.products_low_stock > 0 ||
              stats?.products_out_of_stock > 0) && (
              <div className="alerts-section">
                <h2>
                  <AlertTriangle size={20} />
                  Alertas de Estoque
                </h2>
                <div className="alerts-grid">
                  {stats?.products_low_stock > 0 && (
                    <div className="alert-card warning">
                      <span className="alert-icon">⚠️</span>
                      <div>
                        <strong>{stats.products_low_stock} produtos</strong> com
                        estoque baixo
                      </div>
                    </div>
                  )}
                  {stats?.products_out_of_stock > 0 && (
                    <div className="alert-card danger">
                      <span className="alert-icon">🚨</span>
                      <div>
                        <strong>{stats.products_out_of_stock} produtos</strong>{" "}
                        esgotados
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Gráficos e Tabelas */}
            <div className="charts-section">
              <div className="chart-card">
                <div className="chart-header">
                  <h3>Vendas Diárias</h3>
                  <select
                    value={dateRange}
                    onChange={(e) => setDateRange(Number(e.target.value))}
                    className="date-select"
                  >
                    <option value={7}>Últimos 7 dias</option>
                    <option value={15}>Últimos 15 dias</option>
                    <option value={30}>Últimos 30 dias</option>
                  </select>
                </div>
                <div className="daily-sales-list">
                  {dailySales.map((day, index) => (
                    <div key={index} className="daily-sale-item">
                      <span className="sale-date">
                        {new Date(day.date).toLocaleDateString("pt-BR")}
                      </span>
                      <div className="sale-bars">
                        <div
                          className="sale-bar revenue"
                          style={{ width: `${(day.revenue / 5000) * 100}%` }}
                        >
                          {formatCurrency(day.revenue)}
                        </div>
                        <div
                          className="sale-bar orders"
                          style={{ width: `${(day.orders / 20) * 100}%` }}
                        >
                          {day.orders} pedidos
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="chart-card">
                <h3>Vendas por Categoria</h3>
                <div className="category-list">
                  {salesByCategory.map((cat, index) => (
                    <div key={index} className="category-item">
                      <div className="category-header">
                        <span className="category-name">{cat.category}</span>
                        <span className="category-revenue">
                          {formatCurrency(cat.revenue)}
                        </span>
                      </div>
                      <div className="category-stats">
                        <span>{cat.products_count} produtos</span>
                        <span>{cat.total_sold} unidades</span>
                      </div>
                      <div className="category-bar">
                        <div
                          className="bar-fill"
                          style={{ width: `${(cat.revenue / 5000) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Produtos mais vendidos e estoque baixo */}
            <div className="tables-section">
              <div className="table-card">
                <h3>Produtos Mais Vendidos</h3>
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Produto</th>
                      <th>Categoria</th>
                      <th>Vendidos</th>
                      <th>Receita</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topProducts.map((product) => (
                      <tr key={product.id}>
                        <td>{product.name}</td>
                        <td>{product.category}</td>
                        <td>{product.total_sold} un</td>
                        <td>{formatCurrency(product.revenue)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="table-card">
                <h3>Estoque Baixo</h3>
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Produto</th>
                      <th>Estoque</th>
                      <th>Ação</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lowStockProducts.map((product) => (
                      <tr key={product.id}>
                        <td>{product.name}</td>
                        <td>
                          <span
                            className={`stock-badge ${product.stock === 0 ? "out" : "low"}`}
                          >
                            {product.stock}
                          </span>
                        </td>
                        <td>
                          <button
                            className="action-btn"
                            onClick={() => {
                              setEditingStock(product.id);
                              setNewStockValue(product.stock);
                            }}
                          >
                            <Edit size={14} />
                            Ajustar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {activeTab === "products" && (
          <div className="products-section">
            <div className="section-header">
              <h2>Gerenciar Produtos</h2>
              <button className="add-product-btn">+ Novo Produto</button>
            </div>

            <table className="admin-table products-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Produto</th>
                  <th>Categoria</th>
                  <th>Preço</th>
                  <th>Estoque</th>
                  <th>Vendidos</th>
                  <th>Receita</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td>#{product.id}</td>
                    <td>{product.name}</td>
                    <td>{product.category}</td>
                    <td>{formatCurrency(product.price)}</td>
                    <td>
                      {editingStock === product.id ? (
                        <div className="stock-edit">
                          <input
                            type="number"
                            value={newStockValue}
                            onChange={(e) =>
                              setNewStockValue(Number(e.target.value))
                            }
                            min="0"
                          />
                          <button onClick={() => handleStockUpdate(product.id)}>
                            <Save size={14} />
                          </button>
                          <button onClick={() => setEditingStock(null)}>
                            <X size={14} />
                          </button>
                        </div>
                      ) : (
                        <span
                          className={`stock-badge ${product.stock <= 5 ? "low" : ""}`}
                        >
                          {product.stock}
                        </span>
                      )}
                    </td>
                    <td>{product.total_sold}</td>
                    <td>{formatCurrency(product.revenue)}</td>
                    <td>
                      <button className="action-btn">
                        <Edit size={14} />
                        Editar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "users" && (
          <div className="users-section">
            <h2>Usuários Cadastrados</h2>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nome</th>
                  <th>Email</th>
                  <th>Admin</th>
                  <th>Data de Cadastro</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>#{user.id}</td>
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td>
                      {user.is_admin ? (
                        <span className="admin-badge">Admin</span>
                      ) : (
                        <span className="user-badge">Usuário</span>
                      )}
                    </td>
                    <td>
                      {new Date(user.created_at).toLocaleDateString("pt-BR")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "reports" && (
          <div className="reports-section">
            <h2>Relatórios</h2>
            <div className="reports-grid">
              <div className="report-card">
                <h3>Relatório de Vendas</h3>
                <p>Período: Últimos 30 dias</p>
                <div className="report-stats">
                  <div>Total: {formatCurrency(stats?.total_revenue)}</div>
                  <div>Pedidos: {stats?.total_orders}</div>
                </div>
                <button className="download-btn">Baixar PDF</button>
              </div>

              <div className="report-card">
                <h3>Relatório de Estoque</h3>
                <p>Produtos com estoque baixo: {stats?.products_low_stock}</p>
                <p>Produtos esgotados: {stats?.products_out_of_stock}</p>
                <button className="download-btn">Baixar PDF</button>
              </div>

              <div className="report-card">
                <h3>Relatório de Usuários</h3>
                <p>Total: {stats?.total_users} usuários</p>
                <p>Novos este mês: 0</p>
                <button className="download-btn">Baixar PDF</button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal de ajuste de estoque */}
      {editingStock && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Ajustar Estoque</h3>
            <p>Produto: {products.find((p) => p.id === editingStock)?.name}</p>
            <input
              type="number"
              value={newStockValue}
              onChange={(e) => setNewStockValue(Number(e.target.value))}
              min="0"
              className="stock-input"
            />
            <div className="modal-actions">
              <button
                onClick={() => handleStockUpdate(editingStock)}
                className="save-btn"
              >
                Salvar
              </button>
              <button
                onClick={() => setEditingStock(null)}
                className="cancel-btn"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
