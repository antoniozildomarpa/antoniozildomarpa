"""Imagem sintética tipo Sentinel-2 (B04, B08, SCL e TCI) em volta da área de teste."""
import sys, numpy as np
from osgeo import gdal, ogr, osr
gdal.UseExceptions()
area, saida = sys.argv[1], sys.argv[2]
ds = ogr.Open(area); lyr = ds.GetLayer(0); f0 = next(iter(lyr)); g = f0.GetGeometryRef().Clone()
src = lyr.GetSpatialRef(); src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
utm = osr.SpatialReference(); utm.ImportFromEPSG(32721); utm.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
g.Transform(osr.CoordinateTransformation(src, utm))
x0, x1, y0, y1 = g.GetEnvelope(); b = 3000
x0, x1, y0, y1 = (x0 - b) // 10 * 10, (x1 + b) // 10 * 10, (y0 - b) // 10 * 10, (y1 + b) // 10 * 10
w, h = int((x1 - x0) / 10), int((y1 - y0) / 10)
gt = (x0, 10, 0, y1, 0, -10)
yy, xx = np.mgrid[0:h, 0:w]
rng = np.random.default_rng(1)
cls = np.full((h, w), 5)                                   # floresta
cx, cy = w // 2, h // 2
cls[(xx > cx - 60) & (xx < cx + 120) & (yy > cy - 80) & (yy < cy + 60)] = 3   # pasto no meio da área
cls[(np.hypot(xx - (cx - 40), yy - (cy + 70)) < 45)] = 4                     # regeneração
cls[(np.abs(yy - (cy - 20) - 0.3 * (xx - cx)) < 3)] = 2                     # estrada
cls[(xx > cx + 40) & (xx < cx + 90) & (yy > cy - 60) & (yy < cy - 20)] = 2  # solo exposto
cls[(np.abs(xx - (60 + 0.2 * yy)) < 6)] = 1                                  # rio a oeste
ndvi_alvo = {1: -0.15, 2: 0.15, 3: 0.42, 4: 0.66, 5: 0.84}
nir_alvo = {1: 0.03, 2: 0.22, 3: 0.28, 4: 0.30, 5: 0.32}
ndvi = np.vectorize(ndvi_alvo.get)(cls) + rng.normal(0, 0.035, (h, w))
nir = np.vectorize(nir_alvo.get)(cls) * (1 + rng.normal(0, 0.05, (h, w)))
red = nir * (1 - ndvi) / (1 + ndvi)
cor = {1: (25, 40, 60), 2: (190, 160, 130), 3: (150, 165, 95), 4: (85, 125, 60), 5: (40, 70, 35)}
rgb = np.stack([np.vectorize(lambda c, k=k: cor[c][k])(cls) for k in range(3)]).astype(float)
rgb += rng.normal(0, 6, rgb.shape)
nevoa = np.hypot(xx - (cx + 150), yy - (cy + 100)) < 25                       # névoa sobre floresta (divergência)
rgb[:, nevoa] = rgb[:, nevoa] * 0.3 + 190
scl = np.full((h, w), 4); scl[cls == 2] = 5; scl[cls == 1] = 6
scl[np.hypot(xx - (cx - 100), yy - (cy - 90)) < 20] = 9                       # nuvem mascarada
def grava(nome, arrs, tipo):
    d = gdal.GetDriverByName("GTiff").Create(f"{saida}/{nome}", w, h, len(arrs), tipo)
    d.SetGeoTransform(gt); d.SetProjection(utm.ExportToWkt())
    for i, a in enumerate(arrs, 1): d.GetRasterBand(i).WriteArray(a)
    d = None
raw = lambda r: np.clip((r + 0.1) * 10000, 1, 65535).astype("uint16")
grava("S2_2025-07-19_B04.tif", [raw(red)], gdal.GDT_UInt16)
grava("S2_2025-07-19_B08.tif", [raw(nir)], gdal.GDT_UInt16)
grava("S2_2025-07-19_SCL.tif", [scl.astype("uint8")], gdal.GDT_Byte)
grava("S2_2025-07-19.tif", [np.clip(rgb[k], 1, 255).astype("uint8") for k in range(3)], gdal.GDT_Byte)
print(w, h)
