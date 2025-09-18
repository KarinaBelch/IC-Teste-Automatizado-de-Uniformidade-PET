# IC-Teste-Automatizado-de-Uniformidade-PET
Iniciação Cientifica do curso de Engenharia Biomédica da UFABC | Teste Automatizado de Uniformidade para Instrumentação de Positron Emission Tomography (PET)

Link do aplicativo:
https://ic-teste-automatizado-de-uniformidade-pet.streamlit.app/


Propósito: Este aplicativo permite o processamento automatizado de imagens PET (volumétricas, compostas de vários cortes) adquiridas usando o fantoma cilíndrico Standard Uptake Value (SUV). As imagens são processadas usando os métodos de Miller (citação [1]) e Hasford (citação [2]), e os resultados produzidos constituem valores estatísticos dos pixels em cada fatia (valores máximos e mínimos, média e desvio padrão dentro de cada ROI, conforme definido pelo método ([1] ou [2]). Esses resultados podem ser visualizados na tela deste aplicativo Silverlit e, em seguida, exportados para um arquivo de valores separados por vírgula (.csv) para análise posterior (por exemplo, no LibreOffice Calc ou Microsoft Excel).

Potenciais benefícios do uso deste software para análise de imagens fantasmas de SUVs:
Os potenciais benefícios deste trabalho para o físico médico incluem a eliminação do cálculo manual desses valores estatísticos, que podem ser consideráveis, da variação inter/intraoperador e de erros devido à operação manual. Além disso, como o aplicativo fornece os resultados para dois métodos diferentes, o método de Miller [1] pode ser usado para encontrar onde surge qualquer divergência em relação ao esperado (ou seja, região da imagem), enquanto o método de Hasford [2] usa regiões muito menores para análise e espera-se que seja mais sensível.