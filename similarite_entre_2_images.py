import cv2 as cv
import numpy as np
import os
from scipy.spatial import distance
from tabulate import tabulate

def calculate_histogram(image, M=32):
    # Convertir en espace couleur HSV
    hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    
    # Calculer les histogrammes pour chaque canal
    hist = [cv.calcHist([hsv_image], [i], None, [256], [0, 256]) for i in range(3)]
    
    # Réduire les histogrammes
    reduced_hist = np.zeros((3, M))
    for i in range(3):
        for j in range(M):
            reduced_hist[i, j] = np.sum(hist[i][j * (256 // M):(j + 1) * (256 // M)])
    
    return reduced_hist.flatten()

def calculate_hu_moments(image):
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    moments = cv.moments(gray_image)
    hu_moments = cv.HuMoments(moments).flatten()
    return hu_moments

def calculate_color_distance(hist1, hist2):
    return cv.compareHist(hist1.astype(np.float32), hist2.astype(np.float32), cv.HISTCMP_CHISQR)

def calculate_shape_distance(hu1, hu2):
    return distance.euclidean(hu1, hu2)

def calculate_global_similarity(hist1, hu1, hist2, hu2, w1=0.5, w2=0.5):
    color_distance = calculate_color_distance(hist1, hist2)
    shape_distance = calculate_shape_distance(hu1, hu2)
    return w1 * color_distance + w2 * shape_distance

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv.imread(os.path.join(folder, filename))
        if img is not None:
            images.append((filename, img))
    return images

def find_closest_images(query_image_path, folder, N=5, w1=0.5, w2=0.5):
    query_image = cv.imread(query_image_path)
    if query_image is None:
        print('Could not open or find the query image!')
        return []
    
    query_hist = calculate_histogram(query_image)
    query_hu = calculate_hu_moments(query_image)
    
    images = load_images_from_folder(folder)
    distances = []
    
    for filename, img in images:
        img_hist = calculate_histogram(img)
        img_hu = calculate_hu_moments(img)
        distance = calculate_global_similarity(query_hist, query_hu, img_hist, img_hu, w1, w2)
        distances.append((filename, distance))
    
    distances.sort(key=lambda x: x[1])
    return distances[:N]

# Chemins des images et dossier
query_image_path = 'F:\github.com_extension\indexation_document\data\obj1__95.png'
images_folder = 'F:\github.com_extension\indexation_document\data'

# Trouver les N images les plus proches
N = 5
closest_images = find_closest_images(query_image_path, images_folder, N)

# Afficher les résultats
headers = ["Filename", "Distance"]
print(tabulate(closest_images, headers=headers, tablefmt="grid"))
