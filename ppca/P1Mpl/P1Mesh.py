# Imports
import os
from typing import Dict
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

mpl.use("Agg")

from ppca.P1Utils.P1PCALine import PCALine
from ppca.P1Backend.P1DataObject import P1DataObject

def mesh_plot(outfile: str, indata: Dict, save = False, **kwargs) -> plt.figure:
    """
    Generates a sequence (downcore) mesh plot.

    Keywords:
        outfile: full path to file, format will be determined from file extension (str)
        indata: 
            Dictionary with the numpy arrays of the following parameters:
                Samples: vector of SampleID/Depth.
                Centers: vector of window centers.
                Steps: vector of all steps.
                M: Magnetization matrix with observations in rows, windows in columns.
                Inclination: Inclination matrix with observations in rows, windows in columns.
                Declination: Declination matrix with observations in rows, windows in columns.
                MADp: medium angular deviation, prolate matrix with observations in rows, windows in columns.
                MADo: medium angular deviation, oblate matrix with observations in rows, windows in columns.
        save: save the plot (bool, default: False)
        **kwargs:
            figure: matplotlib figure instance (default: None)
            figsize: size of figure in inches (tuple, default: (5, 6))
            dpi: resolution of figure (float, default: 300)
            NRM: plot NRM (bool, default: True)
            Incl: plot Inclination (bool, default: True)
            Decl: plot Declination (bool, default: True)
            MADp: plot MADp (bool, default: True)
            MADo: plot MADo (bool, default: True)
            invertY: invert order of samples (bool, default: True)
            ylabel: label for y-axis (str, default: "")

    Returns:
        matplotlib figure instance.
    """
    # Set style
    plt.style.use("./ppca/P1Mpl/styles/sequence.mplstyle")

    # Set parameters
    if "figure" not in kwargs:
        kwargs["figure"] = None
    if "figsize" not in kwargs:
        kwargs["figsize"] = (5, 6)
    if "dpi" not in kwargs:
        kwargs["dpi"] = 300
    if "NRM" not in kwargs:
        kwargs["NRM"] = True
    if "NRM_unit" not in kwargs:
        kwargs["NRM_unit"] = ""
    if "Incl" not in kwargs:
        kwargs["Incl"] = True
    if "Decl" not in kwargs:
        kwargs["Decl"] = True
    if "MADp" not in kwargs:
        kwargs["MADp"] = True
    if "MADo" not in kwargs:
        kwargs["MADo"] = True
    if "ylabel" not in kwargs:
        kwargs["ylabel"] = ""
    
    if all (par == False in kwargs for par in ("NRM", "Incl", "Decl", "MADp", "MADo")):
        # Nothing to plot, return
        return
    else:
        cols = [kwargs["NRM"], kwargs["Incl"], kwargs["Decl"], kwargs["MADp"], kwargs["MADo"]]
        indices = [i+1 for i, x in enumerate(cols) if x == True]

    if "invertY" not in kwargs:
        kwargs["invertY"] = True

    # Prepare figure
    ncols = cols.count(True)
    ax = [None] * ncols
    grid = gridspec.GridSpec(1, ncols)
    if kwargs["figure"] != None:
        fig = kwargs["figure"]
    else:
        fig = plt.figure(figsize = kwargs["figsize"], dpi = kwargs["dpi"])

    # Add subplots and data
    for n in range(ncols):
        # Add axis and data
        ax[n] = fig.add_subplot(grid[0, n])
        #ax[n].plot(indata[:, indices[n]], indata[:,0], 'o-', clip_on = False)
        x = indata["Centers"]
        y = indata["Samples"]
        cmap = "PRGn"
        vmin = None
        vmax = None
        if indices[n] == 1: # NRM
            x = indata["Steps"]
            c = indata["M"] / np.amax(indata["M"], axis = 0)
            cmap = "tab20c"
        elif indices[n] == 2: # Inclination
            c = indata["Inclination"]
            vmin = -90
            vmax = 90
        elif indices[n] == 3: # Declination
            c = indata["Declination"]
            vmin = 0
            vmax = 360
        elif indices[n] == 4: # MADp
            c = indata["MADp"]
            cmap = "hot"
        elif indices[n] == 5: # MADo
            c = indata["MADo"]
            cmap = "hot"

        mesh = ax[n].pcolormesh(x, y, c, cmap = cmap, norm = None, edgecolor = None, vmin = vmin, vmax = vmax)

        # Set spines according to column
        if n == 0:
            ax[n].spines["left"].set_visible(True)
            ax[n].spines["left"].set_position(("outward", 5))
            ax[n].tick_params(axis='y', left = True)
            ax[n].set_ylabel(kwargs["ylabel"])
        elif n == ncols - 1:
            ax[n].spines["right"].set_visible(True)
            ax[n].spines["right"].set_position(("outward", 5))
            ax[n].tick_params(axis='y', right = True)
            ax[n].set_ylabel(kwargs["ylabel"])
            ax[n].yaxis.set_label_position("right")

        # Check where x-axis goes and adjust
        if (n % 2) == 0:
            # Bottom
            ax[n].spines["bottom"].set_visible(True)
            ax[n].spines["bottom"].set_position(("outward", 5))
            ax[n].tick_params(axis='x', bottom = True, labelbottom = True)
            ax[n].xaxis.set_label_position("top")
            loc = "upper center"
            y_adjust = 0.115
        else:
            # Top
            ax[n].spines["top"].set_visible(True)
            ax[n].spines["top"].set_position(("outward", 5))
            ax[n].tick_params(axis='x', top = True, labeltop = True)
            ax[n].xaxis.set_label_position("bottom")
            loc = "lower center"
            y_adjust = -0.115
        
        # Invert y-axis if desired and set limits to min - max
        ax[n].set_ylim([indata["Samples"].min(), indata["Samples"].max()])
        if kwargs["invertY"]: ax[n].invert_yaxis()

        # Set specific parameters
        if indices[n] == 1:
            ax[n].set_xlabel("M/M$_0$")
        if indices[n] == 2: # Inclination
            #ax[n].set_xlim([-90, 90])
            #ax[n].set_xticks([-90,0,90])
            ax[n].set_xlabel("Inclination (°)")
        elif indices[n] == 3: # Declination
            #ax[n].set_xlim([0, 360])
            #ax[n].set_xticks([0,180,360])
            ax[n].set_xlabel("Declination (°)")
        elif indices[n] == 4: # MADp
            ax[n].set_xlabel("MADp (°)")
        elif indices[n] == 5: # MADp
            ax[n].set_xlabel("MADo (°)")

        cax = inset_axes(ax[n], width="100%",  height="2%",  loc=loc, bbox_to_anchor=(0, y_adjust, 1, 1), bbox_transform = ax[n].transAxes)
        fig.colorbar(mesh, cax = cax, orientation = "horizontal")
        if loc == "upper center":
            cax.tick_params(axis='x', top = True, bottom = False, labeltop = True, labelbottom = False)
            cax.xaxis.set_label_position("top")

        ax[n].set_xlim([indata["Steps"].min(), indata["Steps"].max()])
    for n in range(1, ncols-1):
        ax[n].set_yticklabels('')

    ax[ncols-1].yaxis.set_label_position("right")
    ax[ncols-1].tick_params(labelleft=False, labelright=True)

    # Draw figure so we can change tick labels
    fig.canvas.draw()

    # Save figure
    if save:
        fig.savefig(outfile, dpi = 300)
    
    return fig