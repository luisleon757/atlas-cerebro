import json, struct, numpy as np, nibabel as nib, trimesh
from scipy import ndimage
from skimage import measure

D = 'dl/fs/'
OUT = 'out/'
REG = ['frontal', 'parietal', 'temporal', 'occipital', 'cerebelo', 'tronco', 'otras', 'hipocampo', 'amigdala', 'talamo', 'basales', 'calloso', 'ventriculos']
COL = {'hipocampo': '#ff5fa2', 'amigdala': '#ff3b30', 'talamo': '#00b8d9', 'basales': '#7ccf3a', 'calloso': '#e0a458', 'ventriculos': '#4fc3f7', 'frontal': '#3d7bff', 'parietal': '#f2b705', 'temporal': '#19b37a', 'occipital': '#a05cf0',
       'cerebelo': '#ff7a2f', 'tronco': '#e8436a', 'otras': '#d9b3a8'}
# Desikan-Killiany (orden FreeSurfer con corpus callosum = 4)
DK = {}
for k in [3, 12, 14, 17, 18, 19, 20, 24, 27, 28, 32]: DK[k] = 0
for k in [8, 22, 25, 29, 31]: DK[k] = 1
for k in [1, 6, 7, 9, 15, 16, 30, 33, 34]: DK[k] = 2
for k in [5, 11, 13, 21]: DK[k] = 3

labels = np.loadtxt('dl/aparc_fsa5.csv', dtype=int)
parts = {r: [] for r in REG}  # list of (verts, normals, shade, faces)
pials = []
for hi, h in enumerate(['left', 'right']):
    g = nib.load(D + f'pial_{h}.gii.gz')
    v = g.darrays[0].data.astype(np.float64); f = g.darrays[1].data.astype(np.int64)
    sulc = nib.load(D + f'sulc_{h}.gii.gz').darrays[0].data
    lab = labels[hi * 10242:(hi + 1) * 10242]
    lab = np.where(lab > 35, lab - 35, lab)
    m = trimesh.Trimesh(v, f, process=False)
    pials.append(m)
    nrm = m.vertex_normals
    s = np.clip(sulc / np.percentile(np.abs(sulc), 95), -1, 1)
    shade = 0.82 - 0.22 * s
    vr = np.array([DK.get(int(l), 6) for l in lab])
    fr = vr[f]
    # región de la cara = mayoría de sus vértices
    face_reg = np.where(fr[:, 1] == fr[:, 2], fr[:, 1], fr[:, 0])
    for ri, r in enumerate(REG):
        sel = f[face_reg == ri]
        if not len(sel): continue
        used, inv = np.unique(sel, return_inverse=True)
        parts[r].append((v[used], nrm[used], shade[used], inv.reshape(-1, 3)))

# cerebelo y tronco desde el volumen MNI152
gm = nib.load(D + 'mni_icbm152_gm_tal_nlin_sym_09a_converted.nii.gz')
wm = nib.load(D + 'mni_icbm152_wm_tal_nlin_sym_09a_converted.nii.gz')
A = gm.affine
vol = (gm.get_fdata() + wm.get_fdata()) / 255.0
vol = ndimage.gaussian_filter(vol, 0.8)
mask = vol > 0.45
cortex = np.zeros(mask.shape, bool)
for pm in pials:
    shell = np.zeros(mask.shape, bool)
    pts, _ = trimesh.sample.sample_surface(pm, 1500000, seed=1)
    ii = np.round(pts - A[:3, 3]).astype(int)
    ok = np.all((ii >= 0) & (ii < np.array(mask.shape)), axis=1); ii = ii[ok]
    shell[ii[:, 0], ii[:, 1], ii[:, 2]] = True
    shell = ndimage.binary_closing(shell, iterations=1)
    cortex |= ndimage.binary_fill_holes(shell)
print('cortex vox', cortex.sum())
cortex = ndimage.binary_dilation(cortex, iterations=3)
x, y, z = [np.arange(n) + A[i, 3] for i, n in enumerate(mask.shape)]
X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
rest = mask & ~cortex & (Z < 2)
stem_box = (np.abs(X) <= 14) & (Y >= -44) & (Y <= -8) & (Z <= -2)
stem_box &= ~((Y < -32) & (np.abs(X) > 10))
cereb = rest & ~stem_box & (Y < -30)
stem = rest & stem_box
def largest(m, k=1):
    lab, n = ndimage.label(m)
    if n == 0: return m
    sz = ndimage.sum(m, lab, range(1, n + 1))
    keep = np.argsort(sz)[::-1][:k] + 1
    return np.isin(lab, keep)
core = largest(ndimage.binary_opening(cereb, iterations=4), 1)
cereb = ndimage.binary_closing(cereb & ndimage.binary_dilation(core, iterations=4), iterations=1)
cereb = largest(cereb, 1)
stem = largest(ndimage.binary_opening(stem, iterations=2), 1)
for name, m in [('cerebelo', cereb), ('tronco', stem)]:
    field = ndimage.gaussian_filter(m.astype(float), 1.0)
    vv, ff, nn, _ = measure.marching_cubes(field, 0.5, step_size=1)
    vv = vv + A[:3, 3]
    tm = trimesh.Trimesh(vv, ff[:, ::-1] if False else ff, process=True)
    trimesh.smoothing.filter_taubin(tm, iterations=12)
    # orientar normales hacia fuera
    tm.fix_normals()
    tm = tm.simplify_quadric_decimation(face_count=24000 if name=='cerebelo' else 7000)
    tm.fix_normals()
    print(name, len(tm.vertices), len(tm.faces), tm.is_watertight, tm.bounds.round())
    sh = np.full(len(tm.vertices), 0.86)
    parts[name].append((np.asarray(tm.vertices), np.asarray(tm.vertex_normals), sh, np.asarray(tm.faces)))


# ---- estructuras internas (Harvard-Oxford subcortical, 1 mm) ----
ho = nib.load('dl/atlas_harvard_oxford.nii.gz'); HA = ho.affine; hod = ho.get_fdata(dtype=np.float32)
INT = {'hipocampo': [102, 110], 'amigdala': [103, 111], 'talamo': [97, 106], 'basales': [98, 99, 100, 104, 107, 108, 109, 112], 'ventriculos': [96, 105]}
def mesh_from_mask(m, aff, faces, smooth=10, sigma=0.8):
    field = ndimage.gaussian_filter(m.astype(float), sigma)
    vv, ff, _, _ = measure.marching_cubes(field, 0.5)
    vv = vv @ aff[:3, :3].T + aff[:3, 3]
    tm = trimesh.Trimesh(vv, ff, process=True)
    trimesh.smoothing.filter_taubin(tm, iterations=smooth)
    tm = tm.simplify_quadric_decimation(face_count=faces); tm.fix_normals()
    return tm
for name, ks in INT.items():
    m = np.zeros(hod.shape[:3], bool)
    for k in ks: m |= hod[..., k] >= 50
    tm = mesh_from_mask(m, HA, 6000 if name in ('basales', 'ventriculos') else 3000)
    print(name, len(tm.faces), tm.bounds.round())
    parts[name].append((np.asarray(tm.vertices), np.asarray(tm.vertex_normals), np.full(len(tm.vertices), 0.95), np.asarray(tm.faces)))
# cuerpo calloso: sustancia blanca en la línea media, encima de los ventrículos
wmv = wm.get_fdata() / 255.0
# silueta del corte sagital medio (arco), extruida hacia los lados y recortada con la sustancia blanca
xi = int(np.argmin(np.abs(x)))
mid = (wmv[xi-1:xi+2].mean(0) > 0.5) & (Z[xi] >= -5) & (Z[xi] <= 40) & (Y[xi] >= -50) & (Y[xi] <= 40)
lab_, n_ = ndimage.label(mid); foot = lab_ == (np.argmax(ndimage.sum(mid, lab_, range(1, n_+1))) + 1)
foot = ndimage.binary_dilation(foot, iterations=1)
cc = (wmv > 0.5) & foot[None, :, :] & (np.abs(X) <= 13)
cc = largest(cc, 1)
tm = mesh_from_mask(cc, A, 4000, smooth=12, sigma=1.0)
print('calloso', len(tm.faces), tm.bounds.round())
parts['calloso'].append((np.asarray(tm.vertices), np.asarray(tm.vertex_normals), np.full(len(tm.vertices), 0.95), np.asarray(tm.faces)))

# unir por región y pasar a coordenadas glTF (metros, Y arriba, anterior = -Z)
allv = np.concatenate([p[0] for r in REG for p in parts[r]])
center = (allv.min(0) + allv.max(0)) / 2
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)
meshes = []
for r in REG:
    if not parts[r]: continue
    V, N, S, F = [], [], [], []; off = 0
    for v, n, s, f in parts[r]:
        V.append(v); N.append(n); S.append(s); F.append(f + off); off += len(v)
    V = ((np.concatenate(V) - center) @ R.T) * 0.001
    N = np.concatenate(N) @ R.T
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
    S = np.concatenate(S); F = np.concatenate(F)
    meshes.append(dict(name=r, V=V.astype(np.float32), N=N.astype(np.float32),
                       C=np.repeat(S[:, None], 3, 1).astype(np.float32), F=F.astype(np.uint32)))
    print(r, len(V), len(F))

def hex2lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c]

def write_glb(path, meshes, colored=True):
    bin_ = bytearray(); views = []; accs = []; gm = []; mats = []; nodes = []
    def add(arr, target, comp, typ, minmax=False):
        nonlocal bin_
        while len(bin_) % 4: bin_ += b'\0'
        b = arr.tobytes(); views.append(dict(buffer=0, byteOffset=len(bin_), byteLength=len(b), target=target)); bin_ += b
        a = dict(bufferView=len(views) - 1, componentType=comp, count=len(arr), type=typ)
        if minmax: a['min'] = arr.min(0).tolist(); a['max'] = arr.max(0).tolist()
        accs.append(a); return len(accs) - 1
    for i, m in enumerate(meshes):
        p = add(m['V'], 34962, 5126, 'VEC3', True); n = add(m['N'], 34962, 5126, 'VEC3'); c = add(m['C'], 34962, 5126, 'VEC3')
        ix = add(m['F'].reshape(-1), 34963, 5125, 'SCALAR')
        col = hex2lin(COL[m['name']] if colored else COL['otras'])
        mats.append(dict(name=m['name'], pbrMetallicRoughness=dict(baseColorFactor=col + [1], metallicFactor=0, roughnessFactor=0.6)))
        gm.append(dict(name=m['name'], primitives=[dict(attributes=dict(POSITION=p, NORMAL=n, COLOR_0=c), indices=ix, material=i)]))
        nodes.append(dict(name=m['name'], mesh=i))
    gl = dict(asset=dict(version='2.0', generator='atlas-cerebro'), scene=0, scenes=[dict(nodes=list(range(len(nodes))))],
              nodes=nodes, meshes=gm, materials=mats, accessors=accs, bufferViews=views, buffers=[dict(byteLength=len(bin_))])
    js = json.dumps(gl, separators=(',', ':')).encode()
    while len(js) % 4: js += b' '
    while len(bin_) % 4: bin_ += b'\0'
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_))
    out += struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(bin_), 0x004E4942) + bytes(bin_)
    open(path, 'wb').write(out); print(path, len(out))

write_glb(OUT + 'cerebro.glb', meshes)

# USDZ para iPhone (Vista rápida / AR Quick Look)
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, UsdUtils, Vt
stage = Usd.Stage.CreateNew(OUT + 'cerebro.usdc')
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y); UsdGeom.SetStageMetersPerUnit(stage, 1.0)
root = UsdGeom.Xform.Define(stage, '/Cerebro'); stage.SetDefaultPrim(root.GetPrim())
for m in meshes:
    path = f"/Cerebro/{m['name']}"
    mesh = UsdGeom.Mesh.Define(stage, path)
    mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(m['V']))
    mesh.CreateFaceVertexCountsAttr(Vt.IntArray.FromNumpy(np.full(len(m['F']), 3, np.int32)))
    mesh.CreateFaceVertexIndicesAttr(Vt.IntArray.FromNumpy(m['F'].reshape(-1).astype(np.int32)))
    mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(m['N'])); mesh.SetNormalsInterpolation('vertex')
    mesh.CreateSubdivisionSchemeAttr('none')
    mat = UsdShade.Material.Define(stage, path + '_mat')
    sh = UsdShade.Shader.Define(stage, path + '_mat/PBR'); sh.CreateIdAttr('UsdPreviewSurface')
    c = [int(COL[m['name']][i:i + 2], 16) / 255 for i in (1, 3, 5)]
    sh.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*c))
    sh.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(0.6)
    mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), 'surface')
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)
stage.GetRootLayer().Save()
UsdUtils.CreateNewARKitUsdzPackage(OUT + 'cerebro.usdc', OUT + 'cerebro.usdz')
import os; print('usdz', os.path.getsize(OUT + 'cerebro.usdz'))
