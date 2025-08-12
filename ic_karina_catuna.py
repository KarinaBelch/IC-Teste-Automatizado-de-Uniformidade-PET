# @title Importando Bibliotecas
import funcoes.processamento as funcao

# Instalação de pacotes
#!pip install pynrrd SimpleITK pydicom

# Manipulação de dados e arrays
import numpy as np
import pandas as pd

# Leitura e manipulação de arquivos médicos
# import nrrd
import SimpleITK as sitk
import pydicom

# Manipulação de arquivos e compressão
import os
import zipfile
from io import BytesIO

# Visualização
import matplotlib.pyplot as plt

# Processamento morfológico e preenchimento
from scipy import ndimage

# Acesso a plataforma para deploy do código
import streamlit as st

import shutil

# Parâmetros
dicom_files = []

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
    
    # Mostrar ao usuário quantos arquivos DICOM foram identificados
     st.write("Arquivos DICOM encontrados:", len(dicom_files))
    
     # Ler e ordenar as fatias
     slices, volume = funcao.funcOrdenarFatias(dicom_files)
    
    # Divir o app em duas colunas
     col1, col2 = st.columns(2)

     with col1:
        idx = st.slider("Escolha a fatia:", 0, volume.shape[0] - 1, 0)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(volume[idx], cmap="gray")
        ax.set_title(f"Slice {idx}")
        ax.axis("off")
        st.pyplot(fig)
 
     with col2:
        min_valor = min(np.count_nonzero(volume, axis=(1,2)))
        max_valor = max(np.count_nonzero(volume, axis=(1,2)))
        limiar = st.slider("Selecione o limiar da imagem:", min_value = min_valor, max_value= max_valor)
        
        fatia_contagem, volume_filtrado = funcao.funcFatiaversusContagem(volume, 1000)

        plt.figure(figsize=(10, 5))
        plt.plot(fatia_contagem, label='Original', marker='o')
        plt.axhline(limiar, color='red', linestyle='--', label=f'Limiar = {limiar}')
        plt.xlabel('Fatia')
        plt.ylabel('Contagem')
        plt.title('Contagem por fatia')
        plt.legend()
        plt.grid(True)
        plt.show()


     # Visualização múltipla (fig2)
     st.markdown("---")
     st.subheader(f"Visualização detalhada da fatia {idx}")

     fatia_contagem, volume_filtrado = funcFatiaversusContagem(volume, limiar)

     edges_volume, filled_volume, raio_volume, cx_volume, cy_volume = funcao.funcPreencherVolume(volume. dicom_files)
     edges_volume, filled_volume, raio_volume, cx_volume, cy_volume = funcao.funcPopularArrays(edges_volume, filled_volume, raio_volume, cx_volume, cy_volume)
     imagem_mascara = funcao.funcCriarMascara(volume, filled_volume)
    
     image = volume[idx]

     image_rgb = img_as_float(image)
     edges_rgb = img_as_float(edges_volume[idx])
     filled_rgb = img_as_float(filled_volume[idx])
    
     fig2, axs = plt.subplots(1, 4, figsize=(15, 10))

     axs[0].imshow(image_rgb, cmap='gray')
     axs[0].set_title(f'Imagem Original (slice {idx})')
     axs[0].axis('off')

     axs[1].imshow(edges_rgb, cmap='gray')
     axs[1].set_title('Borda')
     axs[1].axis('off')

     axs[2].imshow(filled_rgb, cmap='gray')
     axs[2].set_title('Borda Reduzida e Preenchida (90%)')
     axs[2].axis('off')

     axs[3].imshow(imagem_mascara[idx], cmap='gray')
     axs[3].set_title('Imagem com a máscara aplicada')
     axs[3].axis('off')

     st.pyplot(fig2)

# @title Obtendo arquivo DICOM



# @title Ordenando as fatias



# @title Declarando os arrays


# @title Populando os arrays


# @title Função para retirar espaços em branco da imagem



# Metodo 1 | Miller | 7 Circulos

# @title Função para criar os 7 círculos
def func_Circulos(imagemCortada):
    diametro = imagemCortada.shape[0]
    nx = ny = diametro

    # Centros e distâncias
    cx = (nx // 2) + 1
    cy = (ny // 2) + 1
    dx = (nx // 3) + 1
    dy = (ny // 3) + 1

    # Raios
    rx = dx / 2
    ry = dy / 2

    x, y = np.meshgrid(np.arange(1, nx+1), np.arange(1, ny+1))

    lista_circulos = []

    for i in [-1, 0, 1]:
        Im = np.zeros((nx, ny))
        Im[((x - cx + i * 2 * rx) ** 2 + (y - cy) ** 2) < rx ** 2] = 1
        lista_circulos.append(Im)

    for i in [-1, 1]:
        Im = np.zeros((nx, ny))
        Im[((x - cx + i * rx) ** 2 + (y - cy + np.sqrt(3) * rx) ** 2) < rx ** 2] = 1
        lista_circulos.append(Im)

    for i in [-1, 1]:
        Im = np.zeros((nx, ny))
        Im[((x - cx + i * rx) ** 2 + (y - cy - np.sqrt(3) * rx) ** 2) < rx ** 2] = 1
        lista_circulos.append(Im)

    return lista_circulos

# @title Aplicando a mascára para cada círculos

# @title Gerando arquivo excel
dados = []

# for i, fatia in enumerate(Im_circulos_volume):  # i = índice da slice
#     for j in range(len(fatia)):  # j = índice do círculo (0 a 7, se você incluiu o unido)
#         imagem_mascarada = fatia[j]

#         # Pega apenas os valores dentro do círculo (ou seja, > 0)
#         valores = imagem_mascarada[imagem_mascarada > 0]

#         # Se não houver valores válidos (ex: tudo 0), use NaN
#         if len(valores) > 0:
#             mean = np.mean(valores)
#             min_val = min(valores)
#             max_val = max(valores)
#             std = np.std(valores)
#         else:
#             mean = min_val = max_val = std = np.nan

#         dados.append({
#             "Name": f"S{i}C{j}",
#             "Slice": i,
#             "Circle": j + 1,  # 1 a 7 (ou 8 se unido)
#             "Mean": mean,
#             "Min": min_val,
#             "Max": max_val,
#             "Std": std
#         })

# df = pd.DataFrame(dados)

# # Salvar como CSV ou Excel
# #df.to_csv("resultados_circulos.csv", index=False)
# df.to_excel("resultados_circulos.xlsx", index=False)

#display(df)

# Metodo 2

## Para encontrar o tamanho do fisico do cilindro, obter um array com os valores da imagem (senograma)
#- Encontrar número de pixels e converter em milimetros utilizando o tamanho do pixel no dicom
#- Qualquer valor em dicom sempre será em mm


# Tamanho do cilindro

# tamanhoPixel = slices[0].PixelSpacing
# print(tamanhoPixel)
# alturaPixel = imagem_cortada_volume[0].shape[0]
# print(alturaPixel)
# alturaMM = alturaPixel * tamanhoPixel[0]
# print(alturaMM)
# larguraPixel = imagem_cortada_volume[0].shape[1]
# print(larguraPixel)
# larguraMM = larguraPixel * tamanhoPixel[1]
# print(larguraMM)


# Obtendo o tamanho do pixel em mm

def funcQuadrados(fatia):
  y_px_mm, x_px_mm = fatia.PixelSpacing

  y_px = x_px = 12 / y_px_mm

  tamanho_total = len(imagem_cortada_volume[1])

  quadrante = np.array([y_px, x_px])
  print(quadrante)

  num_quadrados = int(tamanho_total/quadrante[0])
  num_quadrados

#teste = funcQuadrados(slices[0])

metodo_2 = []

def analisa_uniformidade(i, imagem_completa, tamanho_bloco=3):
    resultados = []

    for i in range(len(imagem_completa)):
      imagem = imagem_completa[i]
      h, w = imagem.shape

      for y in range(0, h, tamanho_bloco):
          for x in range(0, w, tamanho_bloco):
              bloco = imagem[y:y+tamanho_bloco, x:x+tamanho_bloco]

              # Pula blocos com todos os valores 0 (fora da área útil)
              if np.all(bloco == 0):
                  continue

              # Considera apenas os valores maiores que zero
              pixels_validos = bloco[bloco > 0]

              if pixels_validos.size == 0:
                  continue

              resultados.append({
                  "slice": i,
                  "x": x,
                  "y": y,
                  "mean": np.mean(pixels_validos),
                  "min": np.min(pixels_validos),
                  "max": np.max(pixels_validos),
                  "std": np.std(pixels_validos)
              })

    df = pd.DataFrame(resultados)
    return df

#metodo_2 = analisa_uniformidade(i, imagem_cortada_volume, tamanho_bloco=3)

#metodo_2.to_excel("resultados_circulos_metodo_2.xlsx", index=False)

#display(metodo_2)

