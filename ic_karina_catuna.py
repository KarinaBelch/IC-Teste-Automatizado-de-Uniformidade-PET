# @title Importando Bibliotecas

import funcoes.processamento as funcao

# Manipulação de dados e arrays
import numpy as np
import pandas as pd

# Manipulação de arquivos e compressão
import os
import zipfile
from io import BytesIO 
from xlsxwriter import Workbook

# Visualização
import matplotlib.pyplot as plt

# Acesso a plataforma para deploy do código
import streamlit as st

import shutil


# Parâmetros
dicom_files = []
imagem_cortada_volume = []
circulos_volume = []
dados = []

# Streamlit

# # Titulo da página
st.set_page_config(page_title='Projeto de Iniciação Científica', page_icon='🥼', layout='wide')
st.title('Automated Uniformity Testing PET Instrumentation')
st.info('Projeto de Iniciação Cientifica referente ao curso de Engenharia Biomédica da Universidade Federal do ABC.')


# Menu Lateral
st.sidebar.header("Menu")
st.sidebar.caption("Leitura de arquivos DICOM.")


# # Upload do arquivo
uploaded_zip = st.file_uploader(label='Upload your DICOM file:', type="zip")


# Quando o arquivo estiver sido carregado
if uploaded_zip:
     temp_dir = "temp_upload"
 
     # Limpar e criar diretório temporário
     if os.path.exists(temp_dir):
         shutil.rmtree(temp_dir)
     os.makedirs(temp_dir)
 
     # Salvar arquivo zip
     zip_path = os.path.join(temp_dir, "uploaded.zip")
     with open(zip_path, "wb") as f:
         f.write(uploaded_zip.getbuffer())
 
     # Extrair arquivos do zip
     with zipfile.ZipFile(zip_path, "r") as zip_ref:
         zip_ref.extractall(temp_dir)

     # Listar arquivos .dcm
     dicom_files = funcao.funcObterArquivoDicom(temp_dir)

     # Ler e ordenar as fatias
     slices, volume = funcao.funcOrdenarFatias(dicom_files)
    
     # Divir o app em duas colunas
     col1, col2 = st.columns([1,2])

     with col1:
        # Mostrar ao usuário quantos arquivos DICOM foram identificados
        st.write("Slices do arquivo DICOM encontradas:", len(dicom_files))

        idx = st.slider("Slices:", 0, volume.shape[0] - 1, 0)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(volume[idx], cmap="gray")
        ax.set_title(f"Slice {idx}")
        ax.axis("off")
        st.pyplot(fig)
 
     with col2:
        # Mostrar o volume 3D do arquivo DICOM
        st.write("Volume 3D:", volume.shape)  # (profundidade, altura, largura)

        min_valor = min(np.count_nonzero(volume, axis=(1,2)))
        max_valor = max(np.count_nonzero(volume, axis=(1,2)))
        limiar = st.slider("Defina o limiar da imagem:", min_value = min_valor, max_value= max_valor)

        if st.button("Gerar relatório excel"):
            button = True
        else:
            button = False
        
        fatia_contagem, volume_filtrado = funcao.funcFatiaversusContagem(volume, limiar)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(fatia_contagem, label='Original', marker='o')
        ax.axhline(limiar, color='red', linestyle='--', label=f'Limiar = {limiar}')
        ax.set_xlabel('Fatia')
        ax.set_ylabel('Contagem')
        ax.set_title('Contagem por fatia')
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

     if button:
        # Visualização múltipla (fig2)
        st.markdown("---")
        st.subheader(f"Visualização detalhada")

        # Obtendo ROI e aplicando a máscara
        fatia_contagem, volume_filtrado = funcao.funcFatiaversusContagem(volume, limiar)

        dados_volume = funcao.funcPreencherVolume(volume_filtrado)
        dados_volume = funcao.funcPopularArrays(volume_filtrado, dados_volume)
        imagem_mascara = funcao.funcCriarMascara(volume_filtrado, dados_volume['preenchido'])


        for i in range(len(volume_filtrado)):
            imagem_cortada = funcao.funcRecortaPorCirculo(imagem_mascara[i], dados_volume['cx'][i], dados_volume['cy'][i], dados_volume['raio'][i])
            imagem_cortada_volume.append(imagem_cortada)


        # Obtendo dados pelo método 1
        for i in range(len(imagem_cortada_volume)):
            circulos = funcao.funcCirculos(imagem_cortada_volume[i])  # 7 imagens
            imagens_com_circulos = [c * imagem_cortada_volume[i] for c in circulos]

            # Cria a máscara unida
            mascara_unida = np.clip(np.sum(circulos, axis=0), 0, 1)
            imagem_unida = mascara_unida * imagem_cortada_volume[i]

            imagens_com_circulos.append(imagem_unida)  # adiciona como oitava imagem
            circulos_volume.append(imagens_com_circulos)
        
        df = funcao.funcGerarDataframeMetodoUm(circulos_volume)

        if not df.empty:
            st.dataframe(df)

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)


            buffer.seek(0)  # volta para o início do arquivo

            st.download_button(
                label="Download do Excel",
                data=buffer.read(),
                file_name='large_df.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )