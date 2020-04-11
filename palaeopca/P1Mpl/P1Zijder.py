# Imports
import sys
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.patches as mpatches

mpl.use("Agg")

if "PyQt5" in sys.modules:
    from PyQt5.QtWidgets import QApplication

import palaeopca
from palaeopca.P1Utils.P1PCALine import PCALine
from palaeopca.P1Backend.P1DataObject import P1DataObject

def zijder_save(outdir: str, indata: P1DataObject, xh: str="N", xv: str="N", y: str="W", z: str="Up", pbar=None, **kwargs):
    """
    Warpper function to loop through data, generates and saves zijderveld plots

    :type outdir: string
    :type indata: P1DataObject
    :type xh: string
    :type xv: string
    :type y: string
    :type z: string
    :type pbar: P1Progressbar
    
    :param outdir: full path to output directory, will be created if non existant
    :param indata: P1DataObject with all sample data
    :param xh: component to be plotted on x-axis, horizontal projection (N, S, E or W, default: N)
    :param xv: component to be plotted on x-axis, vertical projection (N, S, E or W, default: N)
    :param y: component to be plotted on y-axis, horizontal projection (N, S, E or W, default: W)
    :param z: component to be plotted on y-axis, vertical projection (Up or Down, default: Up)
    :param pbar: progress bar instance, only used in gui mode

    :Keyword Arguments:
        * *figsize* (``tuple``) --
          size of figure in inches (default: (5, 5))
        * *fmt* (``string``) --
          figure format (default: png)
        * *dpi* (``float``) --
          resolution of figure (default: 300)
        * *pca_results* (``numpy.ndarray``) --
          array of pca results [SampleID/Depth, NRM, Inclination, Declination, MADp, MADo, Min step, Max step] (default: None)
        * *pca_anno* (``bool``) --
          annotate plot with pca results, Inc, Dec, MADp and MADo (default: False)
        * *pca_points* (``bool``) --
          mark points used in pca (default: False)
        * *pca_lines* (``bool``) --
          plot largest Eigenvector of pca (default: False)
    """
    # Check dir and create if necessary
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    # Set parameters
    if "figsize" not in kwargs:
        kwargs["figsize"] = (5, 5)
    if "fmt" not in kwargs:
        kwargs["fmt"] = "png"
    if "dpi" not in kwargs:
        kwargs["dpi"] = 300     
    if "pca_results" not in kwargs:
        kwargs["pca_anno"] = False
        kwargs["pca_points"] = False
        kwargs["pca_lines"] = False
        pca_results = False
    else:
        pca_results = True
    if "pca_anno" not in kwargs:
        kwargs["pca_anno"] = False
    if "pca_points" not in kwargs:
        kwargs["pca_points"] = False
    if "pca_lines" not in kwargs:
        kwargs["pca_lines"] = False

    kwargs["units"] = indata.get_units()
    kwargs["pca_steps"] = indata.get_steps()

    # Loop through samples
    pbar_steps = 100 / indata.rowCount()
    new_value = 0
    zijder_kwargs = kwargs.copy()
    for n, sample in enumerate(indata.get_samples()):
        if pca_results:
            zijder_kwargs["pca_results"] = kwargs["pca_results"][n]
            
        outfile = os.path.join(outdir, "Zijder_{0}.{1}".format(sample, kwargs["fmt"]))
        fig = zijder_plot(sample, indata.get_data(sample), xh, xv, y, z, **zijder_kwargs)
        fig.savefig(outfile)
        plt.close(fig)

        if pbar != None:
            new_value += pbar_steps
            if int(new_value) > pbar.progress.value():
                pbar.progress.setValue(int(new_value))
            QApplication.processEvents()

def zijder_plot(sample: str, indata: np.ndarray, xh: str="N", xv: str="N", y: str="W", z: str="Up", **kwargs) -> plt.figure:
    """
    Generates and a zijderveld plot of provided data.

    :type indata: numpy.ndarray
    :type xh: string
    :type xv: string
    :type y: string
    :type z: string
    
    :param indata: numpy array of (x, y, z) data vectors
    :param xh: component to be plotted on x-axis, horizontal projection (N, S, E or W, default: N)
    :param xv: component to be plotted on x-axis, vertical projection (N, S, E or W, default: N)
    :param y: component to be plotted on y-axis, horizontal projection (N, S, E or W, default: W)
    :param z: component to be plotted on y-axis, vertical projection (Up or Down, default: Up)

    :Keyword Arguments:
        * *figure* (``matplotlib.Figure``) --
          matplotlib figure instance (default: None)
        * *figsize* (``tuple``) --
          size of figure in inches (default: (5, 5))
        * *fmt* (``string``) --
          figure format (default: png)
        * *dpi* (``float``) --
          resolution of figure (default: 300)
        * *units* (``string``) --
          units of x, y, z values for labels (default: "")
        * *pca_results* (``numpy.ndarray``) --
          array of pca results [SampleID/Depth, NRM, Inclination, Declination, MADp, MADo, Min step, Max step] (default: None)
        * *pca_steps* (``list``) --
          list of all demagnetization steps (default: [])
        * *pca_anno* (``bool``) --
          annotate plot with pca results, Inc, Dec, MADp and MADo (default: False)
        * *pca_points* (``bool``) --
          mark points used in pca (default: False)
        * *pca_lines* (``bool``) --
          plot largest Eigenvector of pca (default: False)

    :returns: matplotlib figure or axis instance.
    :rtype: matplotlib.Figure or matplotlib.Axis
    """
    # Set style
    plt.style.use("{0}/P1Mpl/styles/zijder.mplstyle".format(palaeopca.basedir))

    # Set parameters
    if "figure" not in kwargs:
        kwargs["figure"] = None
    if "figsize" not in kwargs:
        kwargs["figsize"] = (5, 5)
    if "dpi" not in kwargs:
        kwargs["dpi"] = 300
    if "fmt" not in kwargs:
        kwargs["fmt"] = "png"
    if "units" not in kwargs:
        kwargs["units"] = ""
    if "pca_results" not in kwargs:
        pca_results = False
        kwargs["pca_results"] = None
        kwargs["pca_steps"] = False
        kwargs["pca_anno"] = False
        kwargs["pca_points"] = False
        kwargs["pca_lines"] = False
    else:
        pca_results = True
    if "pca_steps" not in kwargs:
        kwargs["pca_steps"] = []
        kwargs["pca_points"] = False
    if "pca_anno" not in kwargs:
        kwargs["pca_anno"] = False
    if "pca_points" not in kwargs:
        kwargs["pca_points"] = False
    if "pca_lines" not in kwargs:
        kwargs["pca_lines"] = False

    # Prepare figure
    if kwargs["figure"] != None:
        fig = kwargs["figure"]
    else:
        fig = plt.figure(figsize = kwargs["figsize"], dpi = kwargs["dpi"])

    # Check if figure has an axis and create if necessary
    if len(fig.axes) == 0:
        # Add axes
        ax = fig.add_axes([0.18, 0.1, 0.5, 0.75])
        
        # Make axis equal
        ax.set_aspect("equal", anchor = "C", adjustable = "box")
        redraw = False

        # Move spines to origin
        ax.spines["top"].set_position(("data", 0))
        ax.spines["right"].set_position(("data", 0))
    else:
        ax = fig.axes[0]
        redraw = True
    
    # Add data
    data = {
        "N": indata[:, 0],
        "S": -indata[:, 0],
        "E": indata[:, 1],
        "W": -indata[:, 1],
        "Down": indata[:,2],
        "Up": -indata[:,2],
    }

    # Check if lines already exist
    if not redraw:
        h_line = ax.plot(data[xh], data[y], "s--", color = "blue", label = "Horizontal")
        v_line = ax.plot(data[xv], data[z], "^--", color = "red", label = "Vertical")
        hdl = [h_line[0], v_line[0]]
    else:
        ax.get_lines()[0].set_data(data[xh], data[y])
        ax.get_lines()[1].set_data(data[xv], data[z])
        hdl, _ = ax.get_legend_handles_labels()
        hdl = hdl[:2]

    # Mark points
    if pca_results:
        ind = np.logical_and(kwargs["pca_steps"] >= kwargs["pca_results"][6], kwargs["pca_steps"] <= kwargs["pca_results"][7])

    if kwargs["pca_points"] and len(kwargs["pca_steps"]) == indata.shape[0]:
        if not redraw:
            ax.plot(data[xh][ind], data[y][ind], "s", markerfacecolor = "blue")
            ax.plot(data[xv][ind], data[z][ind], "^", markerfacecolor = "red")
        else:
            ax.get_lines()[2].set_data(data[xh][ind], data[y][ind])
            ax.get_lines()[3].set_data(data[xv][ind], data[z][ind])

    # Draw pca lines
    if kwargs["pca_lines"] and len(kwargs["pca_steps"]) == indata.shape[0]:
        # Convert inc and dec to radians
        incRad = np.radians(kwargs["pca_results"][2])
        decRad = np.radians(kwargs["pca_results"][3])

        # Generate dictionary with all possible projections
        direction_mapper = {
            "NN": np.radians(45),
            "NE": (np.pi / 2 + (-1) * decRad),
            "NS": -np.radians(45),
            "NW": -1 * (np.pi / 2 + (-1) * decRad),

            "EN": decRad,#(np.pi / 2 - decRad),
            "EE": np.radians(45),
            "ES": -decRad,
            "EW": -np.radians(45),

            "SN": -np.radians(45),
            "SE": -1 * (np.pi / 2 + (-1) * decRad),
            "SS": np.radians(45),
            "SW": (np.pi / 2 + (-1) * decRad),

            "WN": -decRad,
            "WE": -np.radians(45),
            "WS": decRad,
            "WW": np.radians(45),
            
            "NUp": -1 * (np.pi / 2 + np.arctan(np.sin(incRad) / (np.cos(incRad) * np.cos(decRad)))),
            "NDown": np.pi / 2 + np.arctan(np.sin(incRad) / (np.cos(incRad) * np.cos(decRad))),

            "EUp": -1 * (np.pi / 2 + np.arctan(np.sin(incRad) / (np.cos(incRad) * np.cos(np.pi/2-decRad)))),
            "EDown": (np.pi / 2 + np.arctan(np.sin(incRad) / (np.cos(incRad) * np.cos(np.pi/2-decRad)))),

            "SUp": np.pi / 2 + np.arctan(np.sin(incRad) / (np.cos(incRad) * np.cos(decRad))),
            "SDown": -1 * (np.pi / 2 + np.arctan(np.sin(incRad) / (np.cos(incRad) * np.cos(decRad)))),

            "WUp": (np.pi / 2 + np.arctan(np.sin(incRad) / (np.cos(incRad) * np.cos(np.pi/2-decRad)))),
            "WDown": -1 * (np.pi / 2 + np.arctan(np.sin(incRad) / (np.cos(incRad) * np.cos(np.pi/2-decRad)))),
        }

        # Get line angle for horizontal projection & calculate horizontal projection line parameters
        angleRad = direction_mapper["{0}{1}".format(xh, y)]
        x_h, y_h = PCALine(data[xh][ind], data[y][ind], angleRad, 1.5)

        # Get line angle for horizontal projection & calculate horizontal projection line parameters
        angleRad = direction_mapper["{0}{1}".format(xv, z)]
        x_v, y_v = PCALine(data[xv][ind], data[z][ind], angleRad, 1.5)

        # Draw lines
        if not redraw:
            ax.plot(x_v, y_v, "-", color = "black")
            ax.plot(x_h, y_h, "-", color = "black")
        else:
            if len(ax.get_lines()) == 4:
                ax.get_lines()[2].set_data(x_v, y_v)
                ax.get_lines()[3].set_data(x_h, y_h)
            else:
                ax.get_lines()[4].set_data(x_v, y_v)
                ax.get_lines()[5].set_data(x_h, y_h)

    # Draw figure so we can change tick labels
    ax.relim()
    ax.autoscale()
    fig.canvas.draw()

    # Move scale factor to label
    ax.xaxis.offsetText.set_visible(False)
    ax.yaxis.offsetText.set_visible(False)

    offset = ax.xaxis.get_offset_text().get_text()
    xlabel = xh
    if xh != xv:
        xlabel += ", {0}".format(xv)
    ax.set_xlabel("{0} ({1} {2})".format(xlabel, kwargs["units"], offset))

    offset = ax.yaxis.get_major_formatter().get_offset()
    ylabel = "{0}, {1}".format(y, z)
    ax.set_ylabel("{0} ({1} {2})".format(ylabel, kwargs["units"], offset))

    # Annotate
    sample_patch = mpatches.Patch(alpha = 0, label = sample)
    hdl.append(sample_patch)

    if kwargs["pca_anno"]:
        inc_patch = mpatches.Patch(alpha = 0, label = "Inc: {:.1f} ($^o$)".format(kwargs["pca_results"][2]))
        hdl.append(inc_patch)

        dec_patch = mpatches.Patch(alpha = 0, label = "Dec: {:.1f} ($^o$)".format(kwargs["pca_results"][3]))
        hdl.append(dec_patch)

        madp_patch = mpatches.Patch(alpha = 0, label = "MADp: {:.1f} ($^o$)".format(kwargs["pca_results"][4]))
        hdl.append(madp_patch)

        mado_patch = mpatches.Patch(alpha = 0, label = "MADo: {:.1f} ($^o$)".format(kwargs["pca_results"][5]))
        hdl.append(mado_patch)
        
    # Add Legend
    ax.legend(handles = hdl, loc = "lower left", bbox_to_anchor = (1.02, 0))

    return fig
