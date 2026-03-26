import os
import streamlit as st
import sqlite3
import pandas as pd

# Descobre a pasta exata onde o app.py está
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PASTA_ATUAL, "sistema_escola.db")

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Escolar", page_icon="🏫", layout="wide")

# 2. Inicialização do Banco de Dados
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS salas (nome TEXT PRIMARY KEY)')
    c.execute('''CREATE TABLE IF NOT EXISTS alunos (
                    contrato TEXT PRIMARY KEY,
                    nome TEXT,
                    curso TEXT,
                    sala TEXT,
                    senha TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# 3. Menu Lateral
st.sidebar.title("🏫 Portal Escolar")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Menu de Navegação", 
    ["📊 Dashboard Geral", "🏢 Gerenciar Salas", "📝 Matricular Aluno"]
)

# 4. Tela: Dashboard Geral
if menu == "📊 Dashboard Geral":
    st.title("📊 Dashboard de Alunos")
    
    conn = sqlite3.connect(DB_PATH)
    df_alunos = pd.read_sql_query("SELECT contrato, nome, curso, sala, senha FROM alunos", conn)
    df_salas = pd.read_sql_query("SELECT nome FROM salas", conn)
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Alunos", f"👤 {len(df_alunos)}")
    col2.metric("Salas Ativas", f"🏢 {len(df_salas)}")
    col3.metric("Status", "🟢 Online")
    
    st.divider()
    
    if df_alunos.empty:
        st.info("Nenhum aluno matriculado.")
    else:
        # Filtros
        col_sala, col_exp = st.columns([2, 1])
        with col_sala:
            salas_disponiveis = ["Todas as Salas"] + df_alunos['sala'].unique().tolist()
            filtro_sala = st.selectbox("Filtrar por Sala", salas_disponiveis)
            
        if filtro_sala != "Todas as Salas":
            df_alunos = df_alunos[df_alunos['sala'] == filtro_sala]

        # Exibição da Tabela
        st.dataframe(
            df_alunos, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "contrato": "📋 Contrato",
                "nome": "👤 Aluno",
                "curso": "📚 Curso",
                "sala": "🏫 Sala",
                "senha": "🔑 Senha"
            }
        )
        
        # Botão para Baixar Excel
        csv = df_alunos.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Baixar Lista em CSV (Excel)",
            data=csv,
            file_name='lista_alunos.csv',
            mime='text/csv',
        )

# 5. Tela: Gerenciar Salas
elif menu == "🏢 Gerenciar Salas":
    st.title("🏢 Gestão de Salas")
    with st.container(border=True):
        nova_sala = st.text_input("Nome da nova sala")
        if st.button("➕ Criar Sala", type="primary"):
            if nova_sala:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("INSERT INTO salas (nome) VALUES (?)", (nova_sala,))
                    conn.commit()
                    conn.close()
                    st.success(f"Sala '{nova_sala}' criada!")
                    st.rerun()
                except:
                    st.error("Sala já existe.")

# 6. Tela: Matricular Aluno
elif menu == "📝 Matricular Aluno":
    st.title("📝 Nova Matrícula")
    conn = sqlite3.connect(DB_PATH)
    df_salas = pd.read_sql_query("SELECT nome FROM salas", conn)
    conn.close()
    
    if df_salas.empty:
        st.error("Crie uma sala primeiro.")
    else:
        with st.form("form_matricula", border=True):
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo")
            curso = col2.text_input("Curso")
            contrato = col1.text_input("Nº Contrato")
            sala = col2.selectbox("Sala", df_salas['nome'].tolist())
            senha = st.text_input("Senha", type="default")
            
            if st.form_submit_button("✅ Salvar"):
                if nome and contrato and senha:
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("INSERT INTO alunos VALUES (?, ?, ?, ?, ?)", (contrato, nome, curso, sala, senha))
                        conn.commit()
                        conn.close()
                        st.success("Matriculado!")
                    except:
                        st.error("Erro no contrato.")
