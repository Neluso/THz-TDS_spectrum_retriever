from TDSA import *
from scipy.optimize import differential_evolution


deg_in = 0  # incidence angle in degrees
snell_sin = n_air * sin(deg_in * pi / 180)
# n_subs = 1.17 - 0.0 * 1j  # substrate refractive index -- cork
n_subs = 1e20 - 0.0 * 1j  # substrate refractive index -- metal


# function definitions
def theta(n):
    return arcsin(snell_sin / real(n))


def ct2(n_l, n_l_1):
    n_l *= cos(theta(n_l))
    n_l_1 *= cos(theta(n_l_1))
    return 4 * n_l * n_l_1 / (n_l + n_l_1)**2


def cr_l_1_l(n_l, n_l_1):  # from n_l-1 to n_l
    n_l_1 *= cos(theta(n_l_1))
    n_l *= cos(theta(n_l))
    return (n_l_1 - n_l) / (n_l_1 + n_l)


def phase_factor(n, k, thick, freq):  # theta in radians
    omg = 2 * pi * freq
    thick *= cos(theta(n))
    phi_n = 2 * omg * thick / c_0
    phi_k = 2 * omg * thick / c_0
    return exp(- 1j * phi_n) * exp(- k * phi_k)


def epsilon(e_s, e_inf, tau, freq):  # Debye model
    omg = 2 * pi * freq
    e_w = e_inf + (e_s - e_inf) / (1 + 1j * omg * tau)
    return e_w


def nk_from_eps(e_s, e_inf, tau, freq):
    e_w = epsilon(e_s, e_inf, tau, freq)
    n = sqrt((abs(e_w) + real(e_w)) / 2)
    k = sqrt((abs(e_w) - real(e_w)) / 2)
    return n, k


def H_sim(freq, n, k, thick, d_air):
    
    H_i = cr_l_1_l(n_subs, n - 1j * k)
    rlm1l = cr_l_1_l(n - 1j * k, n_air_cplx)
    tt = ct2(n - 1j * k, n_air_cplx)
    exp_phi = phase_factor(n, k, thick, freq)
    
    H_i = rlm1l + (tt * H_i * exp_phi) / (1 + rlm1l * H_i * exp_phi)
    
    return exp(- 1j * 2 * 2 * pi * freq * d_air / c_0) * H_i


def cost_function(params, *args):
    d_air, e_s, e_inf, tau, thick = params
    E_sam, E_ref_w, freqs = args
    n, k = nk_from_eps(e_s, e_inf, tau, freqs)  # debye model
    H_teo = H_sim(freqs, n, k, thick, d_air)
    E_teo = irfft(H_teo * E_ref_w)
    return sum((E_sam - E_teo)**2)


t0 = time_ns()
out_dir = './output/traces/'

t_ref, E_ref = read_1file('./data/sim_resources/noise_ref.txt')  # t_ref in ps
f_ref, E_ref_w = fourier_analysis(t_ref, E_ref)  # f_ref in THz

t_ref *= 1e-12  # t_ref in s
f_ref *= 1e12   # f_ref in Hz


# material data
e_s_sim = 1.4**2
e_inf_sim = 1.8**2
tau_sim = 1e-12
n_sim, k_sim = nk_from_eps(e_s_sim, e_inf_sim, tau_sim, f_ref)

for d_mat in [0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000]:
    
    print()
    print('Simulating for', d_mat, 'um')
    name_trace = str(d_mat).zfill(4) + '_' + str(e_s_sim) + '_' + str(e_inf_sim) + '_' + str(tau_sim) + '.txt'
    
    d_mat *= 1e-6
    d_air_sim = 0
    
    H_sim_teo = H_sim(f_ref, n_sim, k_sim, d_mat, d_air_sim)
    E_sim_w = H_sim_teo * E_ref_w
    E_sim = irfft(E_sim_w)
    
    print('Saving trace as', name_trace)
    tw = open(out_dir + name_trace, 'w')
    for i in range(E_sim.size):
        tw.write(str(t_ref[i]) + ',' + str(E_sim[i]) + '\n')
    tw.close()
