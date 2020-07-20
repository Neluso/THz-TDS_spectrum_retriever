from TDSA import *
import os


in_dir = './output/traces/'
dir_list = os.listdir(in_dir)


t_ref, E_ref = read_1file('./output/refs/-10_ref.txt')
f_ref, E_ref_w = fourier_analysis(t_ref, E_ref)
# plot(f_ref, unwrap(angle(E_ref_w)), lw=0.5)
plot(f_ref, toDb_0(E_ref_w), lw=0.5)


for file_i in dir_list:
    t_sim, E_sim = read_1file(in_dir + file_i)  # t_ref in s
    f_sim, E_sim_w = fourier_analysis(t_sim, E_sim)  # f_ref in Hz
    # plot(t_sim, E_sim, lw=0.3)
    # plot(f_sim, unwrap(angle(E_sim_w)), lw=0.5)
    plot(f_sim, toDb_0(E_sim_w), lw=0.5)
    # show()
    # quit()
    # plot(f_sim, toDb_0(E_sim_w), lw=0.3)

show()
