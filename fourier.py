import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def plot_image_spectrum(image_path):
    img = Image.open(image_path).convert('L')
    img = np.array(img)

    # Transformata Fouriera 2D na obrazie
    fourier = np.fft.fft2(img)
    # Przesunięcie zerowej częstotliwości do środka widma
    fourier_shifted = np.fft.fftshift(fourier)

    #Widmo amplitudowe
    magnitude = 20 * np.log10(np.abs(fourier_shifted))
    # Faza (kąt) i mapowanie do zakresu 0-255
    phase = np.angle(fourier_shifted)
    fourier_phase = np.asarray((phase + np.pi) / (2 * np.pi) * 255)

    # Odwrotna transformata FFT (tylko część rzeczywista)
    fourier_inverted = np.fft.ifft2(fourier)
    inv_img = np.real(fourier_inverted)

    # Wyświetlanie oryginału, magnitudy i fazy
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    plt.imshow(img, cmap='gray')
    plt.title('Obraz w odcieniach szarości')
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.imshow(magnitude, cmap='gray')
    plt.title('Widmo amplitudowe')
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.imshow(fourier_phase, cmap='gray')
    plt.title('Widmo fazowe')
    plt.axis('off')

    # Porównanie oryginalnego i odtworzonego obrazu
    plt.figure(figsize=(8, 4))
    plt.subplot(1, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title('Obraz w odcieniach szarości')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(inv_img, cmap='gray')
    plt.title('Odwzorowany obraz po odwrotnej transformacie Fouriera')
    plt.axis('off')

    plt.show()
