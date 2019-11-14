from tkinter import Tk
from tkinter.filedialog import askopenfilename
from matplotlib.pyplot import plot, show, legend, xlabel, ylabel, figure, title, savefig
from read_data import read_data
from write_data import write_data
from jepsen_index import jepsen_index
from DPS_functions import *
from aux_functions import *
from numpy import amax
from shutil import copy, move

Tk().withdraw()
ref_file_path = askopenfilename(initialdir='./data', title='Select reference data')
Tk().withdraw()
sam_file_path = askopenfilename(initialdir='./data', title='Select sample data')


t_ref, E_ref = read_data(ref_file_path)
t_sam, E_sam = read_data(sam_file_path)
t_ref *= 1e-12  # seconds
t_sam *= 1e-12  # seconds
thickness = 1.95e-3  # m


nSamp = E_ref.size
nSamp_pow = nextpow2(nSamp)


n, alpha_f = jepsen_index(t_ref, E_ref, t_sam, E_sam, thickness)
f_ref, E_ref_w = fourier_analysis(t_ref, E_ref, nSamp)
f_sam, E_sam_w = fourier_analysis(t_sam, E_sam, nSamp)
f_min_idx, f_max_idx = f_min_max_idx(f_ref)
noisefloor = noise_floor(f_ref, E_ref_w, 4e12)


print('Writting data')
sam_file = sam_file_path.split('/')[-1]
sam_file = sam_file.replace('.', '_')
sam_file = sam_file.replace(' ', '_')
save_path = write_data(f_ref, E_ref_w, f_sam, E_sam_w, sam_file)
move(ref_file_path, save_path)
move(sam_file_path, save_path)


print('Creating plots')


figure()
fig_name = "Spectra"
plot(f_ref[f_min_idx:2*f_max_idx], prettyfy(E_ref_w, amax(E_ref_w))[f_min_idx:2*f_max_idx], label='Reference')
plot(f_sam[f_min_idx:2*f_max_idx], prettyfy(E_sam_w, amax(E_ref_w))[f_min_idx:2*f_max_idx], label='Sample')
plot(f_ref[f_min_idx:2*f_max_idx], prettyfy(noisefloor, amax(E_ref_w))[f_min_idx:2*f_max_idx], 'r--', label='Noise Floor')
xlabel(r'$f (THz)$')
ylabel(r'$E_{\omega} (dB)$')
title(fig_name)
legend()
savefig(save_path + fig_name + '_' + sam_file + '.svg', format='svg')


print('Plotting data')
show()


print('Closing')
