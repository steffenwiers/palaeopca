from ppca.P1Backend.P1Backend import P1Backend

p = P1Backend()
p.load_file("/home/steffen/devCloud/python/PCATools/testdata/testdata.csv", sep = ",", skip_header = 1)
#p.load_file("/home/steffen/ownCloud/PhD/data/cores/PS39/02/cryo/NRM/39_02_NRM.csv", sep = ",", skip_header = 1)

print(p.run_mesh(window = 3, volume = 1))