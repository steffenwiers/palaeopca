from ppca.P1Backend.P1Backend import P1Backend

p = P1Backend()
#p.load_file("/home/steffen/devCloud/python/PCATools/testdata/testdata.csv", sep = ",", skip_header = 1, volume = 7)
#p.load_file("/home/steffen/ownCloud/PhD/data/cores/PS39/02/cryo/NRM/39_02_NRM.csv", sep = ",", skip_header = 1, volume = 7)
p.load_file("/home/steffen/ownCloud/PhD/data/cores/SWERUS_13PC/13PC_NRM.csv", sep = ",", skip_header = 1, volume = 7)

outdata = p.run_mesh(window = 3)

from ppca.P1Mpl.P1Zijder import zijder_save
from ppca.P1Mpl.P1Sequence import sequence_plot
from ppca.P1Mpl.P1Mesh import mesh_plot

mesh_plot("/home/steffen/devCloud/python/PCATools/testdata/PCA_Mesh_13PC.png", outdata, save = True)

#sequence_plot("/home/steffen/devCloud/python/PCATools/testdata/PCA_Best_Fit.png", outdata, save = True, NRM_unit = "A/m", ylabel = "Depth (m)")

"""zijder_save(
    "/home/steffen/devCloud/python/PCATools/testdata/zijder_test", 
    p.get_data(), 
    format = "png", 
    pca_results = outdata, 
    pca_steps = p.get_data().get_steps(),
    pca_anno = True,
    pca_points = True, 
    pca_lines = True
)"""