# Importando bibliotecas
import os                                                        # Operações do sistema operacional       
import pydicom                                                   # Leitura e manipulação de arquivos médicos
import numpy as np                                               # Manipulação de dados e arrays
import pandas as pd                                              # Manipulação e análise de dados
from skimage import img_as_float                                 # Processamento de imagens
from skimage.feature import canny                                # Detecção de bordas
from skimage.transform import hough_circle, hough_circle_peaks   # Transformada de Hough para detecção de círculos
from skimage.draw import disk                                    # Desenho de discos/círculos    

######### Funções de Processamento da Imagem #########

# Função para obter os arquivos DICOM em um array
def funcObterArquivoDicom(dicom_dir):
  dicom_files = []
  for root, dir, files in os.walk(dicom_dir):
      for file in files:
          if file.endswith(".dcm"):
              dicom_files.append(os.path.join(root, file))

  return dicom_files


# Função para ordenar os slices do arquivo DICOM
def funcOrdenarFatias(dicom_files):
  
  # Ordenar por InstanceNumber (ordem axial)
  slices = [pydicom.dcmread(f) for f in dicom_files]
  slices = [s for s in slices if hasattr(s, 'InstanceNumber')]
  slices.sort(key=lambda s: s.InstanceNumber)

  # Converter para volume 3D
  volume = np.stack([s.pixel_array for s in slices])

  return slices, volume


# Função para filtrar fatias com base na contagem de pixels não nulos
def funcFatiaversusContagem(volume, limiar):
  min_limiar = limiar[0]
  max_limiar = limiar[1]
  fatia_contagem = np.count_nonzero(volume, axis=(1,2))         # Conta pixels não nulos em cada fatia
  volume_filtrado = volume[min_limiar : max_limiar+1]              # Filtra o volume com base nos índices válidos

  return fatia_contagem, volume_filtrado


# Prepara array para armazenar volume preenchido
def funcPreencherVolume(volume):
    shape_volume = volume.shape
    num_slices = shape_volume[0]

    dados_volume = {
        'edges': np.zeros(shape_volume, dtype=np.uint8),
        'preenchido': np.zeros(shape_volume, dtype=np.uint8),
        'raio': np.zeros(num_slices),
        'cx': np.zeros(num_slices),
        'cy': np.zeros(num_slices)
    }

    return dados_volume


def funcPopularArrays(volume_filtrado, dados_volume):
    for i in range(volume_filtrado.shape[0]):
        image = volume_filtrado[i]
        image_rgb = img_as_float(image)

        edges, filled, raio, cx, cy = funcMascaraCircularReduzida(image_rgb, scale=0.92)

        dados_volume['edges'][i] = edges
        dados_volume['preenchido'][i] = filled
        dados_volume['raio'][i] = raio
        dados_volume['cx'][i] = cx
        dados_volume['cy'][i] = cy

    return dados_volume

import numpy as np
np_count_nonzero = np.count_nonzero

# Função para Criar a Máscara Reduzida
def funcMascaraCircularReduzida(image_rgb, scale):

    edges = canny(image_rgb, sigma=1.5, low_threshold=0.1, high_threshold=0.3)

    hough_radii = np.arange(8, image_rgb.shape[0] // 2, 1)
    hough_res = hough_circle(edges, hough_radii)

    accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, total_num_peaks=1)

    if len(cx) == 0:
        empty_mask = np.zeros_like(image_rgb, dtype=bool)
        empty_edges = np.zeros_like(image_rgb, dtype=bool)
        return empty_edges, empty_mask, 0, 0, 0

    # Cria círculo com raio reduzido
    r_reduzido = float(radii[0] * scale)
    rr, cc = disk((cy[0], cx[0]), r_reduzido, shape=image_rgb.shape)

    mask = np.zeros_like(image_rgb, dtype=bool)
    mask[rr, cc] = True

    return edges, mask, r_reduzido, cx[0], cy[0]


# Criando a máscara
def funcCriarMascara(volume, filled_volume):
  imagem_mascara = filled_volume*volume
  return imagem_mascara


# Função para remover espaçoes vazios da imagem
def funcRecortaPorCirculo(image, cx, cy, raio):
    h, w = image.shape[:2]

    if (h == 0 or w == 0):
        return np.zeros_like(image)

    # Limites do retângulo
    x_min = max(int(cx - raio + 1), 0)
    x_max = min(int(cx + raio), w)
    y_min = max(int(cy - raio + 1), 0)
    y_max = min(int(cy + raio), h)

    if y_max <= y_min or x_max <= x_min:
      return np.zeros_like(image)

    # Recorta
    recorte = image[y_min:y_max, x_min:x_max]

    return recorte

############ Abordagem de Miller ############

# Função para criar os círculos menores
def funcCirculos(imagemCortada):
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


# Função para criar o círculo central
def func_CirculoCentral(imagemCortada):

    diametro = imagemCortada.shape[0]
    nx = ny = diametro

    # Centros e distâncias
    cx = (nx // 2) + 1
    cy = (ny // 2) + 1
    dx = 16 / 0.4
    dy = 16 / 0.4

    # Raios
    rx = dx / 2
    ry = dy / 2

    x, y = np.meshgrid(np.arange(1, nx+1), np.arange(1, ny+1))

    Im = np.zeros((nx, ny))
    Im[((x - cx) ** 2 + (y - cy) ** 2) < rx ** 2] = 1

    return Im

# Função para gerar o dataframe com os resultados do método 1
def funcGerarDataframeMetodoUm(circulos_volume):
   dados = []
   for i, fatia in enumerate(circulos_volume):  # i = índice da slice
    for j in range(len(fatia)):  # j = índice do círculo
        imagem_mascarada = fatia[j]

        # Pega apenas os valores dentro do círculo (ou seja, > 0)
        valores = imagem_mascarada[imagem_mascarada > 0]

        if len(valores) > 0:
            mean = np.mean(valores)
            min_val = min(valores)
            max_val = max(valores)
            std = np.std(valores)
        else:
            mean = min_val = max_val = std = np.nan

        dados.append({
            "Name": f"S{i}C{j+1}",
            "Slice": i,
            "Circle": j + 1,
            "Mean": mean,
            "Min": min_val,
            "Max": max_val,
            "Std": std
        })

   df = pd.DataFrame(dados)

   return df

# Função para calcular os parâmetros do método de Miller
def funcParametrosMiller(df, fatias):                       

  circulo_central = df[df['Circle'] == 8]                                                               # Filtrando apenas os circulos centrais (16 cm)
  circulo_central_reduzido = circulo_central.iloc[fatias+1 : (len(circulo_central)-fatias)]             # Removendo os slices dos 12mm primeiros e ultimos milimetros
  x_s = circulo_central_reduzido['Mean']                                                                # Obtendo a média dos circulos centrais

  # Cálculo do SUV, Iva
  Iva = x_s.mean()                                       # Cálculo do SUV

  # Cálculo da variação axial na intensidade da imagem
  max_xs = x_s.max()                                     # Valor máximo entre os circulos
  min_xs = x_s.min()                                     # Valor mínimo entre os circulos
  Va = ((max_xs - min_xs) / Iva )* 100                   # Variação Axial na intensidade da imagem


  # Cálculo para obter somente os 40% centrais
  tamanho = len(circulo_central_reduzido)
  centro = tamanho*0.4
  inicio = int((tamanho - centro) // 2)
  fim = int(inicio + tamanho)
  circulo_central_reduzido_2 = circulo_central_reduzido.iloc[inicio:fim]

  # Cálculo da Uniformidade Transversa Integral
  y_s = []

  for i in range(1,8):

    circulo_central_reduzido_2 = df[df['Circle'] == i]                             # Filtrando cada ROI
    media = circulo_central_reduzido_2['Mean']                          # Obtendo a média do ROI
    media_roi = media.mean()                                            # Cálculo da média por ROI
    y_s.append(media_roi)

  max_ys = max(y_s)
  min_ys = min(y_s)
  IUt = ((max_ys - min_ys) / (max_ys + min_ys)) * 100        # Cálculo da Uniformidade Transversa Integral

  dados = []
  dados.append({
      "Volume Averaged (SUV)": Iva,
      "Axial Variation in Image Intensity (%Va)": Va,
      "Transverse integral uniformity (%IUt)": IUt
  })

  dados_df = pd.DataFrame(dados)

  return dados_df


################# Abordagem de Hasford #################

# Função para calcular o tamanho dos quadrados
def funcQuadrados(fatia, roi_mm):
  y_px_mm, x_px_mm = fatia.PixelSpacing

  y_px = x_px = roi_mm / y_px_mm

  tamanho_total = len(fatia)

  quadrante = np.array([y_px, x_px])

  num_quadrados = int(tamanho_total/quadrante[0])
  
  return quadrante[0]

# Função para analisar a uniformidade
def funcAnalisaUniformidade(i, imagem_completa, tamanho_bloco):
    resultados = []

    for i in range(len(imagem_completa)):
      imagem = imagem_completa[i]
      h, w = imagem.shape
      roi = 1

      for y in range(0, h, tamanho_bloco):
          for x in range(0, w, tamanho_bloco):
                 
              if x + tamanho_bloco > w or y + tamanho_bloco > h:
                continue

              bloco = imagem[y:y+tamanho_bloco, x:x+tamanho_bloco]

              # Pula blocos com todos os valores 0 (fora da área útil)
              if np.any(bloco == 0):
                  continue

              # Considera apenas os valores maiores que zero
              pixels_validos = bloco[bloco > 0]

              if pixels_validos.size == 0:
                  continue

              media = np.mean(pixels_validos)
              minimo = np.min(pixels_validos)
              maximo = np.max(pixels_validos)
              desvio_padrao = np.std(pixels_validos)

              nu_1 = ((maximo - media) / media) * 100
              nu_2 = ((media - minimo) / media) * 100
              nu = max(nu_1, nu_2)

              resultados.append({
                  "slice": i,
                  "roi": roi,
                  "x": x,
                  "y": y,
                  "mean": media,
                  "min": minimo,
                  "max": maximo,
                  "std": desvio_padrao,
                  "NU1": nu_1,
                  "NU2": nu_2
              })

              roi = roi + 1

    df = pd.DataFrame(resultados)
    return df


# Função para calcular os parâmetros do método 2
def funcParametros(df):
  
  df_uniformidade = []                                      # Lista para armazenar os resultados de cada slice
  ultimo_slice = df['slice'].iloc[-1]                       # Obtém o número do último slice

  for i in range(ultimo_slice + 1):
    if df[df['slice'] == i].empty:                             # Verifica se o slice atual está vazio
      continue
    slices = df[ df['slice'] == i ]                         # Filtra o DataFrame para a fatia atual
    nu = max(max(slices['NU1']), max(slices['NU2']))        # Calcula o Nonuniformity (NU) máximo entre NU1 e NU2
    n_rois = len(slices)                                    # Número de ROIs na fatia atual
    soma = sum(slices['max'])                               # Soma dos valores máximos das ROIs na fatia atual
    media_global = soma / n_rois                            # Média global dos valores máximos
    somatorio = sum((slices['max'] - media_global)**2)      # Somatório para o cálculo do desvio padrão
    sd_slice = np.sqrt( (1 / (n_rois - 1)) * somatorio)     # Desvio padrão (SD) da fatia atual
    cv_slice = (sd_slice / media_global) * 100              # Coeficiente de variação da uniformidade (CV) da fatia atual

    # Armazena os resultados em uma lista de dicionários
    df_uniformidade.append({
      "Slice": i,
      "Nonuniformities (%NU)": nu,
      "Standard deviation (SD)": sd_slice,
      "Coefficient of uniformity variation (%CV)": cv_slice
    })

  df = pd.DataFrame(df_uniformidade)                        # Cria o DataFrame final
  
  return df