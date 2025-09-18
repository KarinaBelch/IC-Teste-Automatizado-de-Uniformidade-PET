# Importar bibliotecas
import streamlit as st

# Titulo da página (layout)
st.set_page_config(page_title='Projeto de Iniciação Científica', page_icon='🥼', layout='wide')

# Menu Lateral (layout)
st.sidebar.header("Menu")
st.sidebar.caption("Leitura de arquivos DICOM.")

st.title("Dúvidas")

st.markdown("""
Aqui você encontra respostas para as dúvidas mais comuns sobre o uso da aplicação.
""")

st.header("1. Como faço para carregar meus arquivos DICOM?")
st.markdown("""
- Antes de carregar os arquivos, comprima a pasta com os arquivos .dcm (DICOM) em um arquivo .zip.
- Clique no botão "Carregar Arquivos" na barra lateral.
- Selecione o arquivo .zip do seu computador.
- Aguarde o upload ser concluído.
""")

st.header("2. Qual o separador decimal e delimitador dos valores no arquivo CSV?")
st.markdown("""
- O ponto (`.`) é utilizado como separador decimal. Por exemplo: `3.14`.
- O delimitador dos valores no arquivo CSV é a vírgula (`,`).
""")
