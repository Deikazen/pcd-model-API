import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib import cm

# ==========================================
# PENGATURAN AWAL
# ==========================================
init_sigma = 4.0
init_ksize = 25  # Harus ganjil

# Membuat Figure dan Axes (1D dan 3D)
fig = plt.figure(figsize=(14, 7))
fig.canvas.manager.set_window_title('Interaktif: Distribusi Gaussian')

# Menyediakan ruang kosong di bawah grafik untuk meletakkan slider
plt.subplots_adjust(bottom=0.25, wspace=0.3)

ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

# ==========================================
# FUNGSI UNTUK MENGGAMBAR GRAFIK
# ==========================================


def draw_plots(ksize, sigma):
    # Bersihkan plot sebelumnya agar tidak menumpuk saat di-update
    ax1.clear()
    ax2.clear()

    # Menghitung Kernel 1D dan 2D menggunakan OpenCV
    k1d = cv2.getGaussianKernel(ksize, sigma)
    k2d = np.dot(k1d, k1d.T)

    # --- Plot 1: Kurva Lonceng 1D ---
    x_1d = np.arange(-ksize // 2 + 1, ksize // 2 + 1)
    ax1.plot(x_1d, k1d, marker='o', color='b', linewidth=2)
    ax1.set_title(
        f'Gaussian 1D\n(Sigma: {sigma:.2f}, K-Size: {ksize})', fontsize=12)
    ax1.set_xlabel('Jarak dari pusat (pixel)')
    ax1.set_ylabel('Bobot (Weight)')
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Mengunci batas Y agar kita bisa melihat penurunan puncak saat sigma membesar
    # Set max y limit sedikit di atas nilai maksimum awal (saat sigma kecil)
    ax1.set_ylim([0, max(0.1, np.max(k1d) * 1.2)])

    # --- Plot 2: Permukaan 'Gunung' 2D ---
    x_2d, y_2d = np.meshgrid(np.arange(ksize), np.arange(ksize))
    surf = ax2.plot_surface(x_2d, y_2d, k2d, cmap=cm.viridis,
                            linewidth=0, antialiased=True, alpha=0.8)

    ax2.set_title('Gaussian 2D (Permukaan 3D)', fontsize=12)
    ax2.set_xlabel('Sumbu X (pixel)')
    ax2.set_ylabel('Sumbu Y (pixel)')
    ax2.set_zlabel('Bobot')

    # Mengunci batas Z agar efek "ketinggian gunung" terlihat berubah
    ax2.set_zlim([0, max(0.01, np.max(k2d) * 1.5)])


# Gambar plot untuk pertama kalinya
draw_plots(init_ksize, init_sigma)

# ==========================================
# PEMBUATAN SLIDER
# ==========================================
# Menentukan posisi [left, bottom, width, height] untuk area slider
ax_sigma = plt.axes([0.15, 0.10, 0.70, 0.03])
ax_ksize = plt.axes([0.15, 0.05, 0.70, 0.03])

# Membuat objek Slider
# valstep=2 pada ksize memastikan nilainya selalu ganjil (3, 5, 7, ... 51)
slider_sigma = Slider(ax_sigma, 'Sigma (\u03C3)',
                      0.1, 10.0, valinit=init_sigma)
slider_ksize = Slider(ax_ksize, 'Kernel Size', 3, 51,
                      valinit=init_ksize, valstep=2)

# ==========================================
# FUNGSI UPDATE SAAT SLIDER DIGESER
# ==========================================


def update(val):
    # Mengambil nilai terbaru dari slider
    s = slider_sigma.val
    k = int(slider_ksize.val)

    # Memastikan kernel size selalu ganjil (untuk jaga-jaga)
    if k % 2 == 0:
        k += 1

    # Menggambar ulang grafik dengan nilai baru
    draw_plots(k, s)

    # Memperbarui tampilan kanvas
    fig.canvas.draw_idle()


# Menghubungkan slider dengan fungsi update
slider_sigma.on_changed(update)
slider_ksize.on_changed(update)

# Tampilkan jendela GUI Matplotlib
plt.show()
