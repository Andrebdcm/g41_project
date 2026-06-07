# Análise de Dados - Fase 2
# Este script realiza a análise de dados do banco SQLite 'data/publishers_magazines.db' utilizando Pandas e Matplotlib.

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# ## 1. Carregamento dos Dados
print("--- 1. Carregamento dos Dados ---")
conn = sqlite3.connect("data/publishers_magazines.db")
df_transactions = pd.read_sql_query("SELECT * FROM transactions", conn)
df_magazines = pd.read_sql_query("SELECT * FROM magazines", conn)
df_publishers = pd.read_sql_query("SELECT * FROM publishers", conn)
df_warehouses = pd.read_sql_query("SELECT * FROM warehouses", conn)
conn.close()

print("\nTransactions Head:")
print(df_transactions.head())
print("\nMagazines Head:")
print(df_magazines.head())
print("\nPublishers Head:")
print(df_publishers.head())

# ## 2. Análise de Vendas por Categoria de Revista (Requisito 5)
print("\n--- 2. Análise de Vendas por Categoria de Revista (Requisito 5) ---")
# Merge transactions with magazines to get categories
df_tx_mag = df_transactions.merge(df_magazines, on="magazine_id", how="left")
sales_by_category = df_tx_mag.groupby("magazine_category")["amount"].sum().reset_index()
sales_by_category = sales_by_category.sort_values("amount", ascending=False)
print(sales_by_category)

# ## 3. Top 5 Editores por Volume de Vendas (Requisito 5)
print("\n--- 3. Top 5 Editores por Volume de Vendas (Requisito 5) ---")
# Merge transactions with publishers to get names
df_tx_pub = df_transactions.merge(df_publishers, on="publisher_id", how="left")
sales_by_publisher = df_tx_pub.groupby("publisher_name")["amount"].sum().reset_index()
sales_by_publisher = sales_by_publisher.sort_values("amount", ascending=False)
top5_publishers = sales_by_publisher.head(5)
print(top5_publishers)

# ## 4. Visualização Gráfica - Vendas por Categoria (Requisito 6)
print("\n--- 4. Visualização Gráfica - Vendas por Categoria (Requisito 6) ---")
plt.figure(figsize=(10, 6))
plt.bar(sales_by_category["magazine_category"], sales_by_category["amount"], color="skyblue")
plt.title("Total de Vendas por Categoria de Revista")
plt.xlabel("Categoria")
plt.ylabel("Total de Vendas")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
print("Closing/showing Category Sales plot...")
plt.show()

# ## 5. Visualização Gráfica - Distribuição dos 5 Maiores Editores (Requisito 6)
print("\n--- 5. Visualização Gráfica - Distribuição dos 5 Maiores Editores (Requisito 6) ---")
plt.figure(figsize=(8, 8))
plt.pie(top5_publishers["amount"], labels=top5_publishers["publisher_name"], autopct="%1.1f%%", startangle=140)
plt.title("Distribuição das Vendas - Top 5 Editores")
plt.tight_layout()
print("Closing/showing Top 5 Publishers distribution plot...")
plt.show()

# ## 6. Funcionalidade Extra - Filtro de Transações (Requisito 7)
print("\n--- 6. Funcionalidade Extra - Filtro de Transações (Requisito 7) ---")
def filtrar_transacoes(df_transactions, df_publishers, data_inicio=None, data_fim=None, publisher_name=None):
    """
    Filtra transações por intervalo de datas e/ou nome do editor.
    
    Args:
        df_transactions: DataFrame de transações
        df_publishers: DataFrame de editores
        data_inicio: string no formato YYYY/MM/DD ou None
        data_fim: string no formato YYYY/MM/DD ou None
        publisher_name: string com o nome do editor ou None
    
    Returns:
        DataFrame filtrado com informações do editor incluídas.
    """
    df = df_transactions.copy()
    
    # Converter transaction_date para datetime para comparação
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%Y/%m/%d", errors="coerce")
    
    if data_inicio:
        df = df[df["transaction_date"] >= pd.to_datetime(data_inicio)]
    if data_fim:
        df = df[df["transaction_date"] <= pd.to_datetime(data_fim)]
    
    # Merge com publishers para filtrar por nome
    df = df.merge(df_publishers, on="publisher_id", how="left")
    
    if publisher_name:
        df = df[df["publisher_name"].str.contains(publisher_name, case=False, na=False)]
    
    return df

# Exemplo de uso:
resultado = filtrar_transacoes(df_transactions, df_publishers, data_inicio="2022/01/01", data_fim="2022/12/31", publisher_name="Hawkins")
print(resultado)
