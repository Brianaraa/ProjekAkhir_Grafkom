import json
import os

class SaveLoadManager:
    """
    Manajer Persistensi Data.
    Bertanggung jawab untuk serialisasi objek OOP ke JSON dan 
    deserialisasi JSON kembali menjadi objek hidup.
    """
    
    # Registry untuk memetakan nama string di JSON ke Kelas Python asli
    # Ini memungkinkan sistem Load mengenali objek buatan A dan AY secara dinamis.
    _shape_registry = {}

    @classmethod
    def register_shape(cls, shape_name, shape_class):
        """Mendaftarkan kelas bentuk baru ke dalam sistem Load."""
        cls._shape_registry[shape_name] = shape_class
        print(f"[System] Registered shape type: {shape_name}")

    @classmethod
    def save_project(cls, shapes_list, filename="project_paint.json"):
        """
        Menyimpan seluruh objek di kanvas ke file JSON.
        """
        try:
            # Mengubah setiap objek menjadi dictionary menggunakan method to_dict() dari base.py
            serialized_data = [shape.to_dict() for shape in shapes_list]
            
            with open(filename, 'w') as f:
                # Menggunakan indent agar file JSON mudah dibaca manusia (debugging)
                json.dump(serialized_data, f, indent=4)
                
            print(f"[System] Sukses: {len(shapes_list)} objek disimpan ke {filename}")
            return True
        except Exception as e:
            print(f"[Error] Gagal menyimpan project: {e}")
            return False

    @classmethod
    def load_project(cls, filename="project_paint.json"):
        """
        Memuat data dari JSON dan mengubahnya kembali menjadi objek OOP.
        """
        if not os.path.exists(filename):
            print(f"[Error] File {filename} tidak ditemukan.")
            return []

        try:
            with open(filename, 'r') as f:
                raw_data = json.load(f)
            
            reconstructed_shapes = []
            
            for item in raw_data:
                # Ambil nama kelas dari data JSON
                type_name = item.get("type")
                
                # Cari kelas yang sesuai di dalam registry
                shape_class = cls._shape_registry.get(type_name)
                
                if shape_class:
                    # Instansiasi objek baru berdasarkan data JSON
                    # Menggunakan unpacking (**item) untuk memasukkan atribut secara otomatis
                    # Catatan: to_dict() harus konsisten dengan parameter __init__
                    
                    # Kita hapus kunci 'type' karena tidak ada di __init__
                    params = item.copy()
                    params.pop("type", None)
                    
                    # Konversi warna kembali ke tuple (JSON menyimpannya sebagai list)
                    if "color" in params:
                        params["color"] = tuple(params["color"])
                    
                    # Buat objek asli
                    obj = shape_class(**params)
                    reconstructed_shapes.append(obj)
                else:
                    print(f"[Warning] Tipe objek '{type_name}' tidak terdaftar di registry.")

            print(f"[System] Sukses: {len(reconstructed_shapes)} objek dimuat kembali.")
            return reconstructed_shapes

        except Exception as e:
            print(f"[Error] Gagal memuat project: {e}")
            return []