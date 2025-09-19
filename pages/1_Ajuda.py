# Importar bibliotecas
import streamlit as st
from PIL import Image

# Titulo da página (layout)
st.set_page_config(page_title='Projeto de Iniciação Científica', page_icon='🥼', layout='wide')

# Menu Lateral (layout)
st.sidebar.header("Menu")
st.sidebar.caption("Leitura de arquivos DICOM.")


tab1, tab2, = st.tabs(['Português', 'Inglês'])

#### Versão em Potuguês
with tab1:
    st.markdown("**Idioma selecionado: Português**")
    st.subheader("Propósito")
    st.markdown("""
                Este aplicativo permite o processamento automatizado de imagens PET (volumétricas, compostas de vários cortes) adquiridas usando o fantoma cilíndrico Standard Uptake Value (SUV). As imagens são processadas usando os métodos de Miller (citação [1]) e Hasford (citação [2]), e os resultados produzidos constituem valores estatísticos dos pixels em cada fatia (valores máximos e mínimos, média e desvio padrão dentro de cada ROI, conforme definido pelo método ([1] ou [2]). Esses resultados podem ser visualizados na tela deste aplicativo Streamlit e, em seguida, exportados para um arquivo de valores separados por vírgula (.csv) para análise posterior (por exemplo, no LibreOffice Calc ou Microsoft Excel).
                """
    )
    st.subheader("Potenciais benefícios do uso deste software para análise de imagens fantasmas de SUVs")
    st.markdown("""
Os potenciais benefícios deste trabalho para o físico médico incluem a eliminação do cálculo manual desses valores estatísticos, que podem ser consideráveis, da variação inter/intraoperador e de erros devido à operação manual. Além disso, como o aplicativo fornece os resultados para dois métodos diferentes, o método de Miller [1] pode ser usado para encontrar onde surge qualquer divergência em relação ao esperado (ou seja, região da imagem), enquanto o método de Hasford [2] usa regiões muito menores para análise e espera-se que seja mais sensível.
                """)
    st.markdown("---")
    st.title("Dúvidas")
    st.markdown("""
Aqui você encontra respostas para as dúvidas mais comuns sobre o uso da aplicação.
""")
    
    st.header("1. Como faço para carregar meus arquivos DICOM?")
    st.markdown("""
                O aplicativo só consegue carregar um único arquivo.
Como é necessário analisar várias fatias no formato DICOM, antes de carregar, compacte a pasta com os arquivos .dcm (DICOM) em um arquivo .zip (por exemplo, utilizando o programa 7zip no Windows ou no Linux via linha de comando com o comando zip).
            - Clique no botão "Carregar Arquivos" na barra lateral.
            - Selecione o arquivo .zip do seu computador.
            - Aguarde o upload ser concluído.
    """)

    st.header("2. Qual é o formato do arquivo CSV (comma separated values)?")
    st.markdown("""
                O arquivo gerado pelo programa está no formato comma separated values (extensão .csv).
É um arquivo de texto que pode ser aberto diretamente no LibreOffice Calc ou Microsoft Excel para análises adicionais ou geração de gráficos. \n
                
            - Separador decimal: o ponto (.) é utilizado como separador decimal (como é comum em países de língua inglesa). \n
                
            - Exemplo: o número π é 3.14159265... \n
                
            - Separador de campos: os campos são separados por vírgula (,), como indica o próprio nome comma separated values. \n 
                
            - Assim, a sequência dos primeiros quatro múltiplos de 1/2 apareceria como: \n
                
               ``0.0, 0.5, 1.0, 1.5``
    """)



##### Versão em Inglês
with tab2:
    st.markdown("**Selected Language: English**")
    st.subheader("Purpose")

    st.write("""
            This app allows automated image processing of a PET image (volumetric, composed of various slices) acquired using the cylindrical Standard Uptake Value (SUV) phantom.  Images are processed using the methods of Miller (citation [1]) and Hasford (citation [2]) , and results produced, which constitute statistical values of the pixels in each slice (maximum and minimum values, mean and standard deviation within each ROI as defined by the method ([1] or [2]).  These results can be viewed on the screen in this Streamlit app and then exported to a comma separated value file (.csv) for further analysis (for example, in Libreoffice Calc or Microsoft Excel).
        """)
    st.subheader("Potential benefits of using this software for analysis of SUV phantom images")
    st.markdown("""
            The potential benefits of this work to the medical physicist include elimination of manual calculation of these statistical values, which can be considerable, inter / intra operator variation and errors due to manual operation.  Moreover, since the app provides the results for two different methods, the method of Miller [1], can be used to encounter where any divergence from expected arise (i.e. region of image) whereas the method of Hasford [2] uses much smaller regions for analysis and is expected to be more sensitive. 
""")
    st.markdown("---")
    st.title("FAQ")
    st.markdown("""Here you can find answers to the most common questions about using the application.
""")