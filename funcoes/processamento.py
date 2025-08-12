# Manipulação de arquivos e compressão
import os
import zipfile
from io import BytesIO

# Leitura e manipulação de arquivos médicos
# import nrrd
import SimpleITK as sitk
import pydicom

# Manipulação de dados e arrays
import numpy as np
import pandas as pd

# Processamento de imagens
from PIL import Image
from skimage import color, img_as_ubyte, img_as_float
from skimage.feature import canny
from skimage.transform import hough_circle, hough_circle_peaks, hough_ellipse
from skimage.draw import circle_perimeter, ellipse_perimeter
from skimage.draw import polygon
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

  print("Volume 3D:", volume.shape)  # (profundidade, altura, largura)

  return slices, volume

def funcFatiaversusContagem(volume, limiar):
  fatia_contagem = np.count_nonzero(volume, axis=(1,2))
  indices_validos = np.where(fatia_contagem >= limiar)[0]
  volume_filtrado = volume[indices_validos]

  return fatia_contagem, volume_filtrado

# @title Função para Criar a Máscara
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

def funcPreencherVolume(volume, dicom_files):
  edges_volume = np.zeros_like(volume, dtype=np.uint8)
  filled_volume = np.zeros_like(volume, dtype=np.uint8)
  raio_volume = np.zeros(len(dicom_files))
  cx_volume = np.zeros(len(dicom_files))
  cy_volume = np.zeros(len(dicom_files))

  return edges_volume, filled_volume, raio_volume, cx_volume, cy_volume

def funcPopularArrays(volume, edges_volume, filled_volume, raio_volume, cx_volume, cy_volume):
  for i in range(volume.shape[0]):

      image = volume[i]
      image_rgb = img_as_float(image)

      edges, filled, raio, cx, cy = funcMascaraCircularReduzida(image_rgb, scale=0.9)
      edges_volume[i] = edges
      filled_volume[i] = filled
      raio_volume[i] = raio
      cx_volume[i] = cx
      cy_volume[i] = cy

  return edges_volume, filled_volume, raio_volume, cx_volume, cy_volume

# @title Criando a máscara
def funcCriarMascara(volume, filled_volume):
  imagem_mascara = filled_volume*volume
  return imagem_mascara


# Função para remover espaçoes vazios da imagem
def recorta_por_circulo(image, cx, cy, raio):
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