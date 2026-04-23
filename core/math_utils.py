import math

def rotate_3d(x, y, z, angle_x, angle_y, angle_z):
    """
    Fungsi Matriks Rotasi 3D 
    Digunakan oleh semua objek 3D (Kerucut, Tabung, Bola, Balok, Setengah Bola).
    """
    # Rotasi X (Pitch)
    cy, sy = math.cos(angle_x), math.sin(angle_x)
    y1 = y * cy - z * sy
    z1 = y * sy + z * cy
    
    # Rotasi Y (Yaw)
    cx, sx = math.cos(angle_y), math.sin(angle_y)
    x2 = x * cx + z1 * sx
    z2 = -x * sx + z1 * cx
    
    # Rotasi Z (Roll)
    cz, sz = math.cos(angle_z), math.sin(angle_z)
    x3 = x2 * cz - y1 * sz
    y3 = x2 * sz + y1 * cz
    
    return x3, y3, z2

def project_3d_to_2d(x, y, z, canvas_x, canvas_y, fov=400):
    """
    Fungsi Proyeksi Perspektif.
    Mengubah titik (x,y,z) menjadi koordinat (X,Y) layar datar.
    """
    # Faktor perspektif: makin jauh z, makin kecil ukurannya
    factor = fov / (fov + z) if (fov + z) != 0 else 1
    
    # Kalkulasi proyeksi
    # Y dibalik (-y) karena di layar komputer, sumbu Y positif arahnya ke bawah
    px = x * factor + canvas_x
    py = -y * factor + canvas_y
    
    return px, py