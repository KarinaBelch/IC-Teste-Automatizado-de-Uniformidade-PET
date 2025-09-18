# Importando Bibliotecas
import funcoes.processamento as funcao    # Arquivo criado para manter as funções
import numpy as np                        # Manipulação de dados e arrays
import os                                 # Operações do sistema operacional
import zipfile                            # Manipulação de arquivos e compressão
import matplotlib.pyplot as plt           # Processamento e visualização de imagens
import matplotlib.patches as patches      # Desenho de formas geométricas 
import streamlit as st                    # Criação de apps web interativos
import shutil                             # Operações de arquivo de alto nível

#### Setup da Página ####
# Titulo da página (layout)
st.set_page_config(page_title='Projeto de Iniciação Científica', page_icon='🥼', layout='wide')
st.title('Automated Uniformity Testing PET Instrumentation')
st.info('Projeto de Iniciação Cientifica referente ao curso de Engenharia Biomédica da Universidade Federal do ABC.')

# Menu Lateral (layout)
st.sidebar.header("Menu")
st.sidebar.caption("Leitura de arquivos DICOM.")



#### Variáveis Globais ####

# Declarando arrays
dicom_files = []
imagem_cortada_volume = []
circulos_volume = []
dados = []
metodo_hasford = []
df_uniformidade_hasford = []

# Chave para manter o slider visivel
if "mostrar_slider" not in st.session_state:
    st.session_state.mostrar_slider = False


# Upload do arquivo pelo usuário
uploaded_zip = st.file_uploader(label='Upload your DICOM file in .zip:', type="zip")

# Quando o arquivo estiver sido carregado
if uploaded_zip:
     temp_dir = "temp_upload"      # Diretório temporário para armazenar os arquivos extraídos
 
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

     dicom_files = funcao.funcObterArquivoDicom(temp_dir)       # Listar arquivos .dcm
     slices, volume = funcao.funcOrdenarFatias(dicom_files)     # Ordenar as fatias e criar o volume 3D
    
     col1, col2 = st.columns([1,2])                             # Divir a seção no layout da página em duas colunas (layout)

     with col1:
        st.write("Slices do arquivo DICOM encontradas:", len(dicom_files))  # Mostrar ao usuário quantos arquivos DICOM foram identificados (layout)

        idx = st.slider("Slices:", 0, volume.shape[0] - 1, 0)               # Slider para selecionar a fatia

        # Mostrar a fatia selecionada
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(volume[idx], cmap="gray")
        ax.set_title(f"Slice {idx}")
        ax.axis("off")
        st.pyplot(fig)
 
     with col2:
        # Mostrar o volume 3D do arquivo DICOM
        st.write("Volume 3D:", volume.shape)  # (profundidade, altura, largura)

        min_valor = 0                                                                                   # Cálculo do valor mínimo de contagem
        max_valor = max(np.count_nonzero(volume, axis=(1,2)))                                           # Cálculo do valor máximo de contagem
        limiar = st.slider("Defina o limiar da imagem:", min_value = min_valor, max_value= max_valor)   # Slider para definir o limiar

        # Botão para gerar o relatório
        if st.button("Gerar relatório"):
            button = True
            st.session_state.mostrar_slider = True
        else:
            button = False
        
        fatia_contagem, volume_filtrado = funcao.funcFatiaversusContagem(volume, limiar)    # Obter contagem por fatia e volume filtrado

        # Plotar gráfico de contagem por fatia
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(fatia_contagem, label='Original', marker='o')
        ax.axhline(limiar, color='red', linestyle='--', label=f'Limiar = {limiar}')
        ax.set_xlabel('Fatia')
        ax.set_ylabel('Contagem')
        ax.set_title('Contagem por fatia')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
        
     # Se o botão para gerar o relatório for pressionado
     if button:

        with st.spinner("Relatório sendo gerado...", show_time=True):                               # Mostrar spinner enquanto o relatório está sendo gerado

            col1, col2 = st.columns([1,1])                                                          # Divir o app em duas colunas (layout)

            ############### Processamento das imagens ###############            
            dados_volume = funcao.funcPreencherVolume(volume_filtrado)                              # Obtendo dados do volume filtrado
            dados_volume = funcao.funcPopularArrays(volume_filtrado, dados_volume)                  # Popular arrays com os dados do volume filtrado
            imagem_mascara = funcao.funcCriarMascara(volume_filtrado, dados_volume['preenchido'])   # Criar a máscara circular para cada fatia

            # Recortando as imagens com base na máscara circular
            for i in range(len(volume_filtrado)):
                imagem_cortada = funcao.funcRecortaPorCirculo(imagem_mascara[i], dados_volume['cx'][i], dados_volume['cy'][i], dados_volume['raio'][i])
                imagem_cortada_volume.append(imagem_cortada)   

            with col1:

                st.markdown("---")                          # Divisor horizontal (layout)
                st.subheader(f"Abordagem de Miller")        # Subtítulo (layout)

                ####### Abordagem de Miller ###############

                # Para cada fatia, detectar os círculos e criar as imagens com os círculos desenhados
                for i in range(len(imagem_cortada_volume)):
                    circulos = funcao.funcCirculos(imagem_cortada_volume[i])                    # 7 imagens com os círculos desenhados
                    imagens_com_circulos = [c * imagem_cortada_volume[i] for c in circulos]     # Multiplica cada círculo pela imagem cortada

                    # Cria a máscara unida
                    circulo_central = funcao.func_CirculoCentral(imagem_cortada_volume[i])
                    imagem_unida = circulo_central * imagem_cortada_volume[i]

                    imagens_com_circulos.append(imagem_unida)  # adiciona como oitava imagem
                    circulos_volume.append(imagens_com_circulos)
                
                df = funcao.funcGerarDataframeMetodoUm(circulos_volume)            # Gerar DataFrame com os resultados do método de Miller
                df_miller = funcao.funcParametrosMiller(df)                        # Gerar estatísticas do DataFrame do método de Miller

                if not df.empty:
                    st.caption(f"Valores obtidos para cada ROI")
                    st.dataframe(df)
                    st.caption(f"Valores obtidos a partir do Metodo de Miller")
                    st.dataframe(df_miller)


            with col2:

                st.markdown("---")                      # Divisor horizontal (layout)
                st.subheader(f"Abordagem de Hasford")   # Subtítulo (layout)

                ####### Abordagem de Hasford ###############

                tamanho_quadrados = funcao.funcQuadrados(slices[0], roi_mm = 12)    # Definir o tamanho dos quadrados (em pixels) com base na ROI em mm    

                metodo_hasford = funcao.funcAnalisaUniformidade(i, imagem_cortada_volume, int(tamanho_quadrados))  # Analisar a uniformidade usando a abordagem de Hasford
                df_uniformidade_hasford = funcao.funcParametros(metodo_hasford)                                    # Calcular os parâmetros de uniformidade

                if not metodo_hasford.empty:
                    st.caption(f"Valores obtidos para cada ROI")             # Titulo dos valores obtidos de cada ROI (layout)
                    st.dataframe(metodo_hasford)                             # Mostrar os valores obtidos de cada ROI (layout)
                    st.caption(f"Valores estatísticos para cada slice")      # Titulo dos valores estatísticos para cada slice (layout)
                    st.dataframe(df_uniformidade_hasford)                    # Mostrar os valores estatísticos para cada slice (layout)


     ############ Visualização detalhada dos resultados ###############
     if st.session_state.mostrar_slider:

        st.markdown("---")                      # Divisor horizontal (layout)
        st.subheader(f"Visão detalhada")        # Subtítulo (layout)

        ######## Abordagem de Miller ##########
        with st.expander("Abordagem de Miller"):    
        
            for i in range (len(imagem_cortada_volume)):
                fig, axs = plt.subplots(1, 9, figsize=(20, 6))
                axs[0].imshow(imagem_cortada_volume[i], cmap='gray')
                axs[0].set_title(f'Slice {i}', weight='bold', color='black', loc='left', alpha=0.8)
                axs[0].axis('off')

                for j in range(7):
                    axs[j+1].imshow(circulos_volume[i][j], cmap='gray')
                    axs[j+1].set_title(f'Círculo {j+1}', weight='bold', color='black', loc='left', alpha=0.8)
                    axs[j+1].axis('off')
                    axs[j+1].text(0.5, -0.1, f'Min: {df["Min"][j + i*8]:.2f}\nMax: {df["Max"][j + i*8]:.2f}\nMean: {df["Mean"][j + i*8]:.2f}\nStd: {df["Std"][j + i*8]:.2f}', fontsize=12, color='black', ha='center', va='top', transform=axs[j+1].transAxes, backgroundcolor='lightgray')

                axs[8].imshow(circulos_volume[i][7], cmap='gray')
                axs[8].set_title("Círculo de 16cm", weight='bold', color='black', loc='left', alpha=0.8)
                axs[8].axis('off')
                axs[8].text(0.5, -0.1, f'Min: {df["Min"][7 + i*8]:.2f}\nMax: {df["Max"][7 + i*8]:.2f}\nMean: {df["Mean"][7 + i*8]:.2f}\nStd: {df["Std"][7 + i*8]:.2f}', fontsize=12, color='black', ha='center', va='top', transform=axs[8].transAxes, backgroundcolor='lightgray')     
                st.pyplot(fig)


        ######## Abordagem de Hasford ##########
        with st.expander("Abordagem de Hasford"):
            s = 0
            for i in range (len(imagem_cortada_volume)//5):

                fig, ax = plt.subplots(1, 5, figsize=(6, 6))

                for j in range(5):
                    ax[j].imshow(imagem_cortada_volume[s], cmap='gray')

                    metodo_hasford_slice = metodo_hasford[metodo_hasford["slice"] == s]
                    
                    for _, row in metodo_hasford_slice.iterrows():
                        x0, y0 = row["x"], row["y"]
                        rect = patches.Rectangle(
                            (x0-0.5, y0-0.5),         # canto inferior esquerdo
                            tamanho_quadrados,        # largura
                            tamanho_quadrados,        # altura
                            linewidth=0.3,
                            edgecolor="blue",
                            facecolor="none"
                        )
                        ax[j].add_patch(rect) 
                    
                    ax[j].set_title(f'Slice {s}', fontsize=8, pad=8, weight='bold', color='black', loc='left', alpha=0.8)
                    ax[j].text(0.5, -0.1,f'Nonuniformities (%NU): \n{df_uniformidade_hasford["Nonuniformities (%NU)"].values[s]:.2f}%\nStandard deviation (SD): \n{df_uniformidade_hasford["Standard deviation (SD)"].values[s]:.2f}\nCoefficient of uniformity \nvariation (%CV): \n{df_uniformidade_hasford["Coefficient of uniformity variation (%CV)"].values[s]:.2f}', fontsize=4, color='black', ha='center', va='top', transform=ax[j].transAxes, backgroundcolor='lightgray')
                    ax[j].axis('off')
                    s = s+1

                st.pyplot(fig)