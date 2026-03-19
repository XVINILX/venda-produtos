import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import EditProductModal from "../components/admin/EditProductModal";
import CreateProductModal from "../components/admin/CreateProductModal";
import {
  createProduct,
  updateProduct,
  deleteProduct,
} from "../services/product.service";
import {
  BarChart3,
  Package,
  Users,
  ShoppingBag,
  DollarSign,
  AlertTriangle,
  TrendingUp,
  Layers,
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
import "./DashboardPage.css";

const DashboardPage = () => {
  const { user } = useAuth();
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
  const [editingProduct, setEditingProduct] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);

  const [showCreateModal, setShowCreateModal] = useState(false);

  const handleEditProduct = async (productId, updateData) => {
    try {
      const updatedProduct = await updateProduct(productId, updateData);

      // Atualizar lista de produtos
      setProducts((prev) =>
        prev.map((p) => (p.id === productId ? { ...p, ...updatedProduct } : p)),
      );

      // Atualizar também nas listas derivadas
      if (topProducts.some((p) => p.id === productId)) {
        const updatedTopProducts = await getTopSellingProducts(5);
        setTopProducts(updatedTopProducts);
      }

      if (lowStockProducts.some((p) => p.id === productId)) {
        const updatedLowStock = await getLowStockProducts(5);
        setLowStockProducts(updatedLowStock);
      }

      alert("✅ Produto atualizado com sucesso!");
    } catch (error) {
      console.error("Erro ao editar produto:", error);
      alert(
        "❌ Erro ao editar produto: " +
          (error.response?.data?.detail || "Erro desconhecido"),
      );
    }
  };

  // Função para deletar produto
  const handleDeleteProduct = async (productId) => {
    if (!window.confirm("Tem certeza que deseja excluir este produto?")) {
      return;
    }

    try {
      await deleteProduct(productId);

      // Remover da lista
      setProducts((prev) => prev.filter((p) => p.id !== productId));

      // Atualizar estatísticas
      const updatedStats = await getDashboardStats();
      setStats(updatedStats);

      alert("✅ Produto removido com sucesso!");
    } catch (error) {
      console.error("Erro ao deletar produto:", error);
      alert(
        "❌ Erro ao deletar produto: " +
          (error.response?.data?.detail || "Erro desconhecido"),
      );
    }
  };

  // Função para criar produto
  const handleCreateProduct = async (productData) => {
    try {
      const newProduct = await createProduct(productData);

      // Atualizar lista de produtos
      setProducts((prev) => [...prev, newProduct]);

      // Mostrar mensagem de sucesso (opcional)
      alert("✅ Produto criado com sucesso!");
    } catch (error) {
      console.error("Erro ao criar produto:", error);
      alert(
        "❌ Erro ao criar produto: " +
          (error.response?.data?.detail || "Erro desconhecido"),
      );
    }
  };
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
    } catch (error) {
      console.error("Erro ao carregar dados:", error);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    loadData();
  }, []);

  const handleStockUpdate = async (productId, newStock) => {
    try {
      await updateProductStock(productId, newStock);
      // Recarregar dados
      const updatedProducts = await getProductsWithSales();
      setProducts(updatedProducts);
      setEditingStock(null);
      loadData();
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
              <button
                className="add-product-btn"
                onClick={() => setShowCreateModal(true)}
              >
                + Novo Produto
              </button>
              <CreateProductModal
                isOpen={showCreateModal}
                onClose={() => setShowCreateModal(false)}
                onCreate={handleCreateProduct}
              />
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
                          <button
                            onClick={() =>
                              handleStockUpdate(product.id, newStockValue)
                            }
                          >
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
                      <button
                        className="action-btn edit-btn"
                        onClick={() => {
                          setEditingProduct(product);
                          setShowEditModal(true);
                        }}
                      >
                        <Edit size={14} />
                        Editar
                      </button>
                      <button
                        className="action-btn delete-btn"
                        onClick={() => handleDeleteProduct(product.id)}
                      >
                        <X size={14} />
                        Excluir
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
                onClick={() => handleStockUpdate(editingStock, newStockValue)}
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
      <EditProductModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setEditingProduct(null);
        }}
        onEdit={handleEditProduct}
        product={editingProduct}
      />
    </div>
  );
};

export default DashboardPage;
