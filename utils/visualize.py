
import numpy as np

from gocia.data import covalRadii
from gocia.data.colors import jmol_colors
from gocia.geom import get_bondpairs

from ase import Atoms
from ase.build import make_supercell

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from matplotlib.patches import Ellipse, PathPatch

# Predefine some Linear Algebra operations
univ = lambda x: x / np.linalg.norm(x)
rotv = lambda u, a: np.dot(np.array([[np.cos(np.radians(a)), -np.sin(np.radians(a))],\
    [np.sin(np.radians(a)), np.cos(np.radians(a))]]), u )
normalize = lambda x: (x - min(x))/max(x) if max(x)!=0 else np.array([1 for i in x])

def convert_cell(oldCell):
    if len(oldCell[0]) == 1:
        return np.array([[oldCell[0],0,0], [0,oldCell[1],0], [0,0,oldCell[2]]])
    else:
        return oldCell

def adjustColor(color, amount=1):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])

def getHBonds(atoms, allnum, bdpair):
    hbpair=[]
    for i in [i for i in [[i[0], i[1]] for i in get_bondpairs(atoms, 1.5)] if i not in bdpair]:
        elem = [allnum[i[0]], allnum[i[1]]]
        if 1 in elem and (7 in elem or 8 in elem or 9 in elem):
            hbpair.append(i)
    return hbpair

def getPseudoBonds(atoms, allnum, bdpair):
    pbpair=[]
    for i in [i for i in [[i[0], i[1]] for i in get_bondpairs(atoms, 0.9)] if i not in bdpair]:
        elem = [allnum[i[0]], allnum[i[1]]]
        pbpair.append(i)
    return pbpair

def plotAtom(anum, apos, scale=1,cmap=jmol_colors, \
    colorparam=1, linwt=1.5, enlarge=False):
    if enlarge:
        plotRadii = scale * (0.5+covalRadii[anum]/2)
    else:
        plotRadii = scale * covalRadii[anum]
    shape = plt.Circle(
        apos[:2],
        radius = plotRadii, 
        fc=adjustColor(cmap[anum], colorparam),
        ec=adjustColor('k', colorparam),
        linewidth=linwt,
        )
    plt.gca().add_patch(shape)

def plotCircShine(anum, apos, atomscale=1, shift=0.33, scale=0.25, trans=0.33, enlarge=False):
    if enlarge:
        plotRadii = scale * (0.5+covalRadii[anum]/2)
    else:
        plotRadii = scale * covalRadii[anum]
    shape = plt.Circle(
        apos[:2] + np.array([ -shift, shift])*covalRadii[anum],
        radius = plotRadii, 
        fc='w',
        alpha = trans,
        )
    plt.gca().add_patch(shape)

def plotElliShine(anum, apos, atomscale=1, shift=0.4, scale=0.5, rot=-45, trans=0.33, enlarge=False):
    if enlarge:
        plotRadii = scale * (0.5+covalRadii[anum]/2)
    else:
        plotRadii = scale * covalRadii[anum]
    shape = Ellipse(
        apos[:2] + np.array([ -shift, shift])*covalRadii[anum]*atomscale,
        width = 0.66 * atomscale * plotRadii, 
        height = scale * atomscale * covalRadii[anum], 
        angle = rot,
        fc='w',
        alpha = trans,
        )
    plt.gca().add_patch(shape)

def plotBondHalf(allnum, allpos, bdpair, begnum, atomscale, bdrad,\
     mode, cmap=jmol_colors, colorparam=1, linwt=1.5):
    for b in bdpair:
        if begnum in b[:2]:
            if begnum == b[0]: a1, a2 = b[0], b[1]
            if begnum == b[1]: a1, a2 = b[1], b[0]
            if mode=='high':
                if allpos[a1][2] > allpos[a2][2]: continue
            if mode=='low':
                if allpos[a1][2] < allpos[a2][2]: continue
            beg, end = allpos[a1][:2], allpos[a2][:2]
            bdvec = univ(end - beg)
            mid=(beg + atomscale*(covalRadii[allnum[a1]]-covalRadii[allnum[a2]])*bdvec + end)/2
            # mid = (allpos[a1][:2]*covalRadii[a1] + allpos[a2][:2]*covalRadii[a2]) /(covalRadii[a1] + covalRadii[a2])
            if mode=='high': beg = beg + covalRadii[allnum[a1]]*bdvec*atomscale*0.66
            Path = mpath.Path
            path_data = [
                (Path.MOVETO, beg + bdrad*rotv(bdvec, 90)),
                (Path.CURVE4, beg + bdrad*rotv(bdvec, 120)),
                (Path.CURVE4, beg + bdrad*rotv(bdvec, 150)),
                (Path.CURVE4, beg + bdrad*rotv(bdvec, 170)),
                (Path.LINETO, beg + bdrad*rotv(bdvec, 190)),
                (Path.CURVE4, beg + bdrad*rotv(bdvec, 210)),
                (Path.CURVE4, beg + bdrad*rotv(bdvec, 240)),                
                (Path.CURVE4, beg + bdrad*rotv(bdvec, 270)),
                (Path.LINETO, mid + bdrad*rotv(bdvec, 270)),
                (Path.LINETO, mid + bdrad*rotv(bdvec, 90)),
                (Path.CLOSEPOLY, beg + bdrad*rotv(bdvec, 90))
            ]
            codes, verts = zip(*path_data)
            path = mpath.Path(verts, codes)
            patch = PathPatch(
                path,
                fc=adjustColor(cmap[allnum[a1]], colorparam),
                ec=adjustColor('k', colorparam),
                linewidth = linwt,
                )
            plt.gca().add_patch(patch)
            # x, y = zip(*path.vertices); line, = plt.plot(x, y, 'go-')

def plothHbond(allnum, allpos, hbpair, begnum, atomscale, \
    colorparam=1):
    for b in hbpair:
        if begnum in b[:2]:
            if begnum == b[0]: a1, a2 = b[0], b[1]
            if begnum == b[1]: a1, a2 = b[1], b[0]
            if allpos[a1][2] > allpos[a2][2]: continue
            beg, end = allpos[a1][:2], allpos[a2][:2]
            bdvec = univ(end - beg)
            beg = beg + bdvec * atomscale * covalRadii[allnum[a1]]
            end = end - bdvec * atomscale * covalRadii[allnum[a2]]
            dtline = plt.Line2D(
                [beg[0], end[0]],
                [beg[1], end[1]],
                lw=3,
                ls='--',
                alpha=0.75,
                color='k',
                )
            plt.gca().add_line(dtline)

def plotCell(x1, x2, y1, y2, linc = 'k', linwt=1.5):
    cellLine = plt.Line2D([x1,x1], [y1, y2], lw=linwt, color=linc, alpha=0.5); plt.gca().add_line(cellLine)
    cellLine = plt.Line2D([x1,x2], [y2, y2], lw=linwt, color=linc, alpha=0.5); plt.gca().add_line(cellLine)
    cellLine = plt.Line2D([x2,x2], [y2, y1], lw=linwt, color=linc, alpha=0.5); plt.gca().add_line(cellLine)
    cellLine = plt.Line2D([x2,x1], [y1, y1], lw=linwt, color=linc, alpha=0.5); plt.gca().add_line(cellLine)

def drawBSsurf(
    interfc,
    bdcutoff=0.85,
    ascale=0.4,
    brad=0.1,
    outName=None,
    zLim=None,
    pseudoBond = False,
    hBond = False,
    ):
    atoms = interfc.get_allAtoms()
    if zLim is None:
        zLim = [(interfc.get_subPos()[:,2].min() + interfc.get_subPos()[:,2].max()) / 2,
                interfc.get_allPos()[:,2].max()]
    atoms = atoms[[a.index for a in atoms \
        if zLim[0] < interfc.get_allPos()[a.index][2] <= zLim[1]]]
    ori_cell = convert_cell(atoms.get_cell())
    atoms = atoms*[3,3,1]
    atoms.set_pbc([0,0,0])
    atoms = Atoms(sorted(atoms, key=lambda atm: atm.position[2]))
    allpos = atoms.get_positions()
    del atoms[[a.index for a in atoms \
        if (ori_cell[0][0] - 2 > allpos[a.index][0]\
		or  allpos[a.index][0] > ori_cell[0][0]*2 + 2)\
        or (ori_cell[1][1] - 2 > allpos[a.index][1]\
		or  allpos[a.index][1] > ori_cell[1][1]*2 + 2)]]
    allnum = atoms.get_atomic_numbers()
    allpos = atoms.get_positions()
    allz = allpos[:, 2]
    # color gradient according to z
    # if max(allz) - min(allz) < zlim:
    #     allc=[1]*len(allz)

    adsList = interfc.get_adsIndexList()
    bufList = interfc.get_bufferList()
    adsList = [i for i in range(len(atoms)) \
        if atoms.get_positions()[i]-ori_cell[0]-ori_cell[1]\
            in interfc.get_allPos()[adsList]]
    bufList = [i for i in range(len(atoms)) \
        if atoms.get_positions()[i]-ori_cell[0]-ori_cell[1]\
            in interfc.get_allPos()[bufList]]
    allc = [
		1 if i in adsList           # Full color
		else 1.33 if i in bufList   # Shallow color
		else 2.0 for i in range(len(atoms))
	]

    bdpair = [[i[0], i[1]] for i in get_bondpairs(atoms, bdcutoff)]
    hbpair = []
    if hBond:
        hbpair=getHBonds(atoms, allnum, bdpair)
    if pseudoBond:
        hbpair=getPseudoBonds(atoms, allnum, bdpair)
    plotCell(
        ori_cell[0][0] * 1,
        ori_cell[0][0] * 2,
        ori_cell[1][1] * 1,
        ori_cell[1][1] * 2,
        linwt=5)
    for i in range(len(atoms)):
        anum = allnum[i]
        apos = allpos[i]
        plotBondHalf(allnum, allpos, bdpair, i,\
            atomscale=ascale, bdrad=brad, mode='low',\
            colorparam=allc[i], linwt=2.5-allc[i])
        plotAtom(anum, apos, scale=ascale,\
            colorparam=allc[i], linwt=2.5-allc[i], enlarge=True)
        plotElliShine(anum, apos, atomscale=0.4, shift=0.45, scale=0.5)
        plotBondHalf(allnum, allpos, bdpair, i,\
            atomscale=ascale, bdrad=brad, mode='high',\
            colorparam=allc[i], linwt=2.5-allc[i])
        plothHbond(allnum, allpos, hbpair, i,\
            atomscale=ascale)
#    plotCell(ori_cell[0][0], ori_cell[0][0]*2, ori_cell[1][1], ori_cell[1][1]*2)
    plt.axis('scaled')
    plt.xlim(ori_cell[0][0]*1, ori_cell[0][0]*2)
    plt.ylim(ori_cell[1][1]*1, ori_cell[1][1]*2)
    plt.tight_layout()
    plt.axis('off')
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.margins(0,0)
    if outName is not None:
        plt.savefig(outName+'-bs.png', dpi=100, \
            bbox_inches = "tight", transparent=True, pad_inches = 0)
    else:
        plt.show()
    plt.close()

def drawCPK(
    interfc,
    ascale=1,
    outName=None,
    zLim=None,
    ):
    atoms = interfc.get_allAtoms()
    if zLim is None:
        zLim = [(interfc.get_subPos()[:,2].min() + interfc.get_subPos()[:,2].max()) / 2,
                interfc.get_allPos()[:,2].max()]
    atoms = atoms[[a.index for a in atoms \
        if zLim[0] < interfc.get_allPos()[a.index][2] <= zLim[1]]]
    # atoms = atoms[[a.index for a in atoms \
    #     if zLim[0] < allpos[a.index][2] <= zLim[1]]]
    ori_cell = convert_cell(atoms.get_cell())
    atoms_old = atoms.copy()
    atoms = Atoms(sorted(atoms, key=lambda atm: atm.position[2]))
    allnum = atoms.get_atomic_numbers()
    allpos = atoms.get_positions()
    adsList = interfc.get_adsIndexList()
    bufList = interfc.get_bufferList()
    adsList = [i for i in range(len(atoms)) \
        if atoms.get_positions()[i] in interfc.get_allPos()[adsList]]
    bufList = [i for i in range(len(atoms)) \
        if atoms.get_positions()[i] in interfc.get_allPos()[bufList]]
    allc = [
		1 if i in adsList       # Full color
		else 1.33 if i in bufList   # Shallow color
		else 2.0 for i in range(len(atoms))
	]
    plotCell(
        ori_cell[0][0] * 1,
        ori_cell[0][0] * 2,
        ori_cell[1][1] * 1,
        ori_cell[1][1] * 2,
        linwt=5)
    for i in range(len(atoms)):
        anum = allnum[i]
        apos = allpos[i]
        plotAtom(anum, apos, scale=ascale,\
            colorparam=allc[i], linwt=2.5-allc[i])
        plotElliShine(anum, apos, atomscale=ascale, shift=0.45, scale=0.5)
    plt.axis('scaled')
    plt.xlim(ori_cell[0][0]*0, ori_cell[0][0]*1)
    plt.ylim(ori_cell[1][1]*0, ori_cell[1][1]*1)
    plt.tight_layout()
    plt.axis('off')
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.margins(0,0)
    if outName is not None:
        plt.savefig(outName+'-cpk.png', dpi=100, \
            bbox_inches = "tight", transparent=True, pad_inches = 0)
    else:
        plt.show()
    plt.close()

def heatmap(matrix, baseName):
    import matplotlib
    from matplotlib import cm
    import matplotlib.pyplot as plt
    dimension = len(matrix)
    fig, ax = plt.subplots()
    im = ax.imshow(matrix, cmap=cm.Blues)
    fig.colorbar(im)
    ax.tick_params(top=True, bottom=False,
                    labeltop=True, labelbottom=False)
    ax.set_xticks(np.arange(dimension))
    ax.set_yticks(np.arange(dimension))
    # ... and label them with the respective list entries
    ax.set_xticklabels([str(i) for i in np.arange(dimension)])
    ax.set_yticklabels([str(i) for i in np.arange(dimension)])
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right",
            rotation_mode="anchor")
    fig.tight_layout()
    plt.savefig(
        '%s_heat.png'%(baseName),
        dpi=200
        )