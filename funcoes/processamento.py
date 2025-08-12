# Manipulação de arquivos e compressão
import os

# Leitura e manipulação de arquivos médicos
import pydicom

# Manipulação de dados e arrays
import numpy as np
import pandas as pd

# Processamento de imagens
from skimage import img_as_ubyte, img_as_float
from skimage.feature import canny
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.draw import disk

# Função para obter os arquivos DICOM em um array
def funcObterArquivoDicom(dicom_dir):
  dicom_files = []
  for root, dirs, files in os.walk(dicom_dir):
      for file in files:
          if file.endswith(".dcm"):
              dicom_files.append(os.path.join(root, file))

  print("Arquivos DICOM encontrados:", len(dicom_files))

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


def funcFatiaversusContagem(volume, limiar):
  fatia_contagem = np.count_nonzero(volume, axis=(1,2))
  indices_validos = np.where(fatia_contagem >= limiar)[0]
  volume_filtrado = volume[indices_validos]

  return fatia_contagem, volume_filtrado

# Função para Criar a Máscara Reduzida
def funcMascaraCircularReduzida(image_rgb, scale):

    edges = canny(image_rgb, sigma=5, low_threshold=0.1, high_threshold=0.2)

    hough_radii = np.arange(0, image_rgb.shape[0], 1)
    hough_res = hough_circle(edges, hough_radii)

    accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, total_num_peaks=1)

    if len(cx) == 0:
        empty_mask = np.zeros_like(image_rgb, dtype=bool)
        empty_edges = np.zeros_like(image_rgb, dtype=bool)
        return empty_edges, empty_mask, 0, 0, 0

    # Cria círculo com raio reduzido
    r_reduzido = int(radii[0] * scale)
    rr, cc = disk((cy[0], cx[0]), r_reduzido, shape=image_rgb.shape)

    mask = np.zeros_like(image_rgb, dtype=bool)
    mask[rr, cc] = True

    return edges, mask, r_reduzido, cx[0], cy[0]

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

        edges, filled, raio, cx, cy = funcMascaraCircularReduzida(image_rgb, scale=0.9)

        dados_volume['edges'][i] = edges
        dados_volume['preenchido'][i] = filled
        dados_volume['raio'][i] = raio
        dados_volume['cx'][i] = cx
        dados_volume['cy'][i] = cy

    return dados_volume

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


def funcGerarDataframeMetodoUm(circulos_volume):
   dados = []
   for i, fatia in enumerate(circulos_volume):  # i = índice da slice
    for j in range(len(fatia)-1):  # j = índice do círculo
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
            "Name": f"S{i}C{j}",
            "Slice": i,
            "Circle": j + 1,
            "Mean": mean,
            "Min": min_val,
            "Max": max_val,
            "Std": std
        })

   df = pd.DataFrame(dados)

   return df