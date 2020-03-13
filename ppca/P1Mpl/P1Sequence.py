# Imports
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import gridspec

mpl.use("Agg")

from ppca.P1Utils.P1PCALine import PCALine
from ppca.P1Backend.P1DataObject import P1DataObject

def sequence_plot(outfile: str, indata: np.ndarray, save = False, **kwargs) -> plt.figure:
    """
    Generates a sequence (downcore) plot.

    Keywords:
        outfile: full path to file, format will be determined from file extension (str)
        indata: array of pca results [SampleID/Depth, NRM, Inclination, Declination, MADp, MADo, Min step, Max step] (numpy array)
        save: save the plot (bool, default: False)
        **kwargs:
            figure: matplotlib figure instance (default: None)
            figsize: size of figure in inches (tuple, default: (5, 6))
            dpi: resolution of figure (float, default: 300)
            NRM: plot NRM (bool, default: True)
            NRM_unit: units of NRM (str, default: "")
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
        ax[n].plot(indata[:, indices[n]], indata[:,0], 'o-', clip_on = False)

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
            ax[n].xaxis.set_label_position("bottom")
        else:
            # Top
            ax[n].spines["top"].set_visible(True)
            ax[n].spines["top"].set_position(("outward", 5))
            ax[n].tick_params(axis='x', top = True, labeltop = True)
            ax[n].xaxis.set_label_position("top")
        
        # Invert y-axis if desired and set limits to min - max
        ax[n].set_ylim([indata[:,0].min(), indata[:,0].max()])
        if kwargs["invertY"]: ax[n].invert_yaxis()

        # Set specific parameters
        if indices[n] == 2: # Inclination
            ax[n].set_xlim([-90, 90])
            ax[n].set_xticks([-90,0,90])
            ax[n].set_xlabel("Inclination (°)")
        elif indices[n] == 3: # Declination
            ax[n].set_xlim([0, 360])
            ax[n].set_xticks([0,180,360])
            ax[n].set_xlabel("Declination (°)")
        elif indices[n] == 4: # MADp
            ax[n].set_xlabel("MADp (°)")
        elif indices[n] == 5: # MADp
            ax[n].set_xlabel("MADo (°)")

    for n in range(1, ncols-1):
        ax[n].set_yticklabels('')

    ax[ncols-1].yaxis.set_label_position("right")
    ax[ncols-1].tick_params(labelleft=False, labelright=True)

    # Draw figure so we can change tick labels
    fig.canvas.draw()

    # Move offset of NRM axis
    if kwargs["NRM"]:
        ax[0].xaxis.offsetText.set_visible(False)
        offset = ax[0].xaxis.get_offset_text().get_text()
        ax[0].set_xlabel("NRM ({0} {1})".format(kwargs["NRM_unit"], offset))
    
    # Save figure
    if save:
        fig.savefig(outfile, dpi = kwargs["dpi"])
    
    return fig