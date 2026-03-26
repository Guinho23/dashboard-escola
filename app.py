import streamlit as st
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash

# Caminho do banco de dados
DB_PATH = r"C:\Users\Admin\Documents\dash via certa\sistema_escola.db"

# 1. Configuração da Página (Layout Wide para tela cheia)
st.set_page_config(page_title="Gestão Escolar", page_icon="🎓", layout="wide")

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
                    senha_hash TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# 3. Estilização do Menu Lateral
st.sidebar.title("🎓 Portal Escolar")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegação", 
    ["📊 Visão Geral", "🏢 Gerenciar Salas", "📝 Matricular Aluno"]
)
st.sidebar.markdown("---")
st.sidebar.caption("Sistema de Gestão v1.0")

# 4. Tela: Visão Geral (Dashboard)
if menu == "📊 Visão Geral":
    st.title("📊 Visão Geral do Sistema")
    st.markdown("Acompanhe os indicadores e a lista de alunos matriculados.")
    
    conn = sqlite3.connect(DB_PATH)
    df_alunos = pd.read_sql_query("SELECT contrato, nome, curso, sala FROM alunos", conn)
    df_salas = pd.read_sql_query("SELECT nome FROM salas", conn)
    conn.close()
    
    # Cartões de Resumo (KPIs) usando colunas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total de Alunos", value=len(df_alunos))
    with col2:
        st.metric(label="Salas Ativas", value=len(df_salas))
    with col3:
        st.metric(label="Status do Sistema", value="Online 🟢")
        
    st.markdown("---")
    
    if df_alunos.empty:
        st.info("Nenhum aluno cadastrado no momento.")
    else:
        # Filtros organizados
        col_filtro1, col_filtro2 = st.columns([1, 2])
        with col_filtro1:
            salas_disponiveis = ["Todas"] + df_alunos['sala'].unique().tolist()
            filtro_sala = st.selectbox("📌 Filtrar por Sala", salas_disponiveis)
            
        if filtro_sala != "Todas":
            df_alunos = df_alunos[df_alunos['sala'] == filtro_sala]
            
        # Tabela bonitona
        st.dataframe(
            df_alunos, 
            use_container_width=True, 
            hide_index=True, # Esconde aquela coluna de números (0, 1, 2...)
            column_config={
                "contrato": "Nº Contrato",
                "nome": "Nome do Aluno",
                "curso": "Curso Matriculado",
                "sala": "Sala Vinculada"
            }
        )

# 5. Tela: Gerenciar Salas
elif menu == "🏢 Gerenciar Salas":
    st.title("🏢 Gerenciamento de Salas")
    st.markdown("Crie novas turmas ou salas de aula no sistema.")
    
    with st.container(border=True): # Cria uma caixa ao redor do formulário
        nova_sala = st.text_input("Nome da nova sala (ex: Informática - Manhã)")
        
        if st.button("💾 Salvar Sala", type="primary"):
            if nova_sala:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("INSERT INTO salas (nome) VALUES (?)", (nova_sala,))
                    conn.commit()
                    conn.close()
                    st.success(f"Sala '{nova_sala}' registrada com sucesso!")
                except sqlite3.IntegrityError:
                    st.error("⚠️ Esta sala já existe no sistema.")
            else:
                st.warning("⚠️ O nome da sala não pode ficar em branco.")

# 6. Tela: Cadastrar Aluno
elif menu == "📝 Matricular Aluno":
    st.title("📝 Matricular Novo Aluno")
    
    conn = sqlite3.connect(DB_PATH)
    df_salas = pd.read_sql_query("SELECT nome FROM salas", conn)
    conn.close()
    
    if df_salas.empty:
        st.error("⚠️ Nenhuma sala encontrada. Por favor, crie uma sala primeiro no menu 'Gerenciar Salas'.")
    else:
        with st.form("form_cadastro", border=True):
            st.subheader("Dados do Aluno")
            
            # Colocando os campos lado a lado
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo")
                contrato = st.text_input("Número do Contrato")
            with col2:
                curso = st.text_input("Curso")
                sala = st.selectbox("Vincular à Sala", df_salas['nome'].tolist())
                
            st.markdown("---")
            st.subheader("Segurança")
            senha = st.text_input("Senha de Acesso", type="password")
            
            # Botão de envio
            submit = st.form_submit_button("✅ Finalizar Matrícula")
            
            if submit:
                if nome and curso and contrato and senha:
                    senha_protegida = generate_password_hash(senha)
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("INSERT INTO alunos (contrato, nome, curso, sala, senha_hash) VALUES (?, ?, ?, ?, ?)", 
                                  (contrato, nome, curso, sala, senha_protegida))
                        conn.commit()
                        conn.close()
                        st.success(f"🎉 Matrícula de {nome} realizada com sucesso!")
                    except sqlite3.IntegrityError:
                        st.error("⚠️ Já existe um aluno matriculado com este número de contrato.")
                else:
                    st.warning("⚠️ Preencha todos os campos obrigatórios.")