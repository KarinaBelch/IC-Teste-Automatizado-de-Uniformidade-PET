# Importar bibliotecas
import streamlit as st
from PIL import Image

# Titulo da página (layout)
st.set_page_config(page_title='Projeto de Iniciação Científica', page_icon='🥼', layout='wide')

# Menu Lateral (layout)
st.sidebar.header("Automated Uniformity Testing PET Instrumentation")
st.sidebar.caption("Projeto de Iniciação Cientifica referente ao curso de Engenharia Biomédica da Universidade Federal do ABC.")

tab1, tab2, = st.tabs(['Português', 'Inglês'])

#### Versão em Potuguês
with tab1:
    st.markdown("**Idioma selecionado: Português**")
    st.subheader("Propósito")
    st.markdown("""
                Este aplicativo permite o processamento automatizado de imagens PET (volumétricas, compostas de vários cortes) adquiridas usando o fantoma 
                cilíndrico Standard Uptake Value (SUV). As imagens são processadas usando os métodos de Miller [1] e Hasford [2], e os resultados 
                produzidos constituem valores estatísticos dos pixels em cada fatia (valores máximos e mínimos, média e desvio padrão dentro de cada ROI, conforme 
                definido pelo método ([1] ou [2]). Esses resultados podem ser visualizados na tela deste aplicativo Streamlit e, em seguida, exportados para um 
                arquivo de valores separados por vírgula (.csv) para análise posterior (por exemplo, no LibreOffice Calc ou Microsoft Excel).
                """
    )
    st.subheader("Potenciais benefícios do uso deste software para análise de imagens fantasmas de SUVs")
    st.markdown("""
Os potenciais benefícios deste trabalho para o físico médico incluem a eliminação do cálculo manual desses valores estatísticos, que podem ser consideráveis, da variação inter/intraoperador e de erros devido à operação manual. Além disso, como o aplicativo fornece os resultados para dois métodos diferentes, o método de Miller [1] pode ser usado para encontrar onde surge qualquer divergência em relação ao esperado (ou seja, região da imagem), enquanto o método de Hasford [2] usa regiões muito menores para análise e espera-se que seja mais sensível.
                """)
    
    st.caption("""
        Citations:
        1. MA Miller, Focusing on high performance. Philips Advanced Molecular Imaging, Vereos PET/CT, 2016. 
        Disponível em: https://philipsproductcontent.blob.core.windows.net/assets/20170523/360753349c5d4a6aa46ba77c015e75b4.pdf
               
        2. F Hasford, B Van Wyk, and et al. Effect of radionuclide activity concentration on PET-CT image uniformity. World journal of nuclear medicine, 15(2):91—95, 2016. ISSN 1450-1147. doi: 10.4103/1450-1147.167578.)
    """)

    st.markdown("---")
    st.header("Dúvidas")
    st.markdown("""
Aqui você encontra respostas para as dúvidas mais comuns sobre o uso da aplicação.
""")
    
    st.subheader("1. Como faço para carregar meus arquivos DICOM?")
    st.markdown("""
            O aplicativo só consegue carregar um único arquivo.

            Como é necessário analisar várias fatias no formato DICOM, antes de carregar, compacte a pasta com os arquivos ``.dcm`` (DICOM) em um 
            arquivo ``.zip`` (por exemplo, utilizando o programa 7zip no Windows ou no Linux via linha de comando com o comando zip).
            
            1. Clique no botão "Carregar Arquivos" na barra lateral.
                
            2. Selecione o arquivo ``.zip`` do seu computador.
                
            3. Aguarde o upload ser concluído.
    """)

    st.subheader("2. Qual é o formato do arquivo CSV (comma separated values)?")
    st.markdown("""
            O arquivo gerado pelo programa está no formato comma separated values (extensão .csv).
            É um arquivo de texto que pode ser aberto diretamente no LibreOffice Calc ou Microsoft Excel para análises adicionais ou geração de gráficos.
    
            Separador decimal: o ponto ``(.)`` é utilizado como separador decimal (como é comum em países de língua inglesa).
                
            Exemplo: o número π é ``3.14159265...``
                
            Separador de campos: os campos são separados por vírgula ``(,)``, como indica o próprio nome comma separated values.
                
            Assim, a sequência dos primeiros quatro múltiplos de 1/2 apareceria como:
               ``0.0, 0.5, 1.0, 1.5``
    """)



##### Versão em Inglês
with tab2:
    st.markdown("**Selected Language: English**")

    st.subheader("Purpose")
    st.write("""
            This app allows automated image processing of a PET image (volumetric, composed of various slices) acquired using the cylindrical Standard Uptake Value 
             (SUV) phantom.  Images are processed using the methods of Miller [1] and Hasford [2], and results produced, which constitute statistical values of the 
             pixels in each slice (maximum and minimum values, mean and standard deviation within each ROI as defined by the method ([1] or [2]).  These results can 
             be viewed on the screen in this Streamlit app and then exported to a comma separated value file (.csv) for further analysis (for example, in Libreoffice 
             Calc or Microsoft Excel).
        """)
    
    st.subheader("Potential benefits of using this software for analysis of SUV phantom images")
    st.markdown("""
            The potential benefits of this work to the medical physicist include elimination of manual calculation of these statistical values, which can be considerable, 
                inter / intra operator variation and errors due to manual operation. Moreover, since the app provides the results for two different methods, the method 
                of Miller [1], can be used to encounter where any divergence from expected arise (i.e. region of image) whereas the method of Hasford [2] uses much smaller 
                regions for analysis and is expected to be more sensitive. 
    """)
    
    st.caption("""
        Citations:
        1. MA Miller, Focusing on high performance. Philips Advanced Molecular Imaging, Vereos PET/CT, 2016. 
        Disponível em: https://philipsproductcontent.blob.core.windows.net/assets/20170523/360753349c5d4a6aa46ba77c015e75b4.pdf
               
        2. F Hasford, B Van Wyk, and et al. Effect of radionuclide activity concentration on PET-CT image uniformity. World journal of nuclear medicine, 15(2):91—95, 2016. ISSN 1450-1147. doi: 10.4103/1450-1147.167578.)
    """)

    st.markdown("---")

    st.header("FAQ")

    st.markdown("""Here you can find answers to the most common questions about using the application.
""")
    
    st.subheader("1. How do I upload my DICOM files?")
    st.markdown("""
            The app can only load a single file.
            Since multiple slices in DICOM format need to be analyzed, before uploading, compress the folder containing the ``.dcm`` (DICOM) files into a ``.zip`` archive 
                (for example, using 7zip on Windows or the zip command in Linux).

            1. Click on the "Upload Files" button in the sidebar.
            2. Select the ``.zip`` file from your computer.
            3. Wait for the upload to complete.
""")

    st.subheader("2. What is the file format of comma separated values (.csv)?")
    st.markdown("""
            The file produced by the program is in comma separated values format (extension .csv).
            It is a plain text file that can be opened directly in LibreOffice Calc or Microsoft Excel for further analysis or figure generation.
                
            Decimal separator: the dot ``(.)`` is used as the decimal separator (as is common in the English-speaking world).
                
            Example: the number π is ``3.14159265...``
                
            Field separator: the fields are separated by a comma ``(,)``, as indicated by the name comma separated values.
                
            Therefore, the sequence of the first four multiples of one half would appear as:
            ``0.0, 0.5, 1.0, 1.5``
    """)

        

