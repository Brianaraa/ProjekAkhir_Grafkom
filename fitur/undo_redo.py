import copy
from collections import deque

class UndoRedoManager:
    """
    Sistem Manajemen Riwayat (State Machine) menggunakan struktur data Stack.
    Telah dioptimalkan dengan pembatasan memori agar RAM tidak bocor (Memory Leak) 
    saat user melakukan terlalu banyak aksi.
    """
    
    def __init__(self, max_history=30):
        # max_history = batas maksimal 'ingatan' aplikasi. 
        # 30 berarti user bisa Undo maksimal sampai 30 langkah ke belakang.
        self.max_history = max_history
        
        self.undo_stack = deque(maxlen=max_history)  # O(1) append & auto-trim
        self.redo_stack = deque(maxlen=max_history)  # Dibatasi sama seperti undo_stack

    def save_state(self, current_shapes):
        """
        Panggil metode ini SETIAP KALI TERJADI PERUBAHAN pada kanvas.
        (Misal: setelah mouse di-lepas (MOUSEBUTTONUP) saat menggambar/menggeser).
        """
        # 1. Gunakan deepcopy agar kita merekam 'nilai' objek, bukan alamat memorinya
        state_snapshot = copy.deepcopy(current_shapes)
        
        # 2. Masukkan ke tumpukan masa lalu (deque auto-trim jika melebihi maxlen)
        self.undo_stack.append(state_snapshot)
        
        # 3. Aturan Waktu: Jika user melakukan aksi baru, masa depan (redo) hancur/reset
        self.redo_stack.clear()
        
        print(f"[Riwayat] State direkam. Kapasitas Undo: {len(self.undo_stack)}/{self.max_history}")

    def undo(self, current_shapes):
        """
        Mundur satu langkah ke masa lalu (Ctrl + Z).
        """
        if self.can_undo():
            # Simpan state saat ini ke masa depan sebelum mundur
            self.redo_stack.append(copy.deepcopy(current_shapes))
            
            # Ambil state dari masa lalu
            restored_state = self.undo_stack.pop()
            print(f"[Riwayat] Undo berhasil. Sisa langkah: {len(self.undo_stack)}")
            return restored_state
            
        print("[Riwayat] Mentok! Tidak ada riwayat untuk di-Undo.")
        return current_shapes # Kembalikan objek asli jika gagal

    def redo(self, current_shapes):
        """
        Maju satu langkah ke masa depan (Ctrl + Y).
        """
        if self.can_redo():
            # Simpan state saat ini ke masa lalu sebelum maju
            self.undo_stack.append(copy.deepcopy(current_shapes))
            
            # Ambil state dari masa depan
            restored_state = self.redo_stack.pop()
            print(f"[Riwayat] Redo berhasil. Sisa langkah: {len(self.redo_stack)}")
            return restored_state
            
        print("[Riwayat] Mentok! Tidak ada riwayat untuk di-Redo.")
        return current_shapes

    def can_undo(self):
        """Metode helper untuk UI: Mengecek apakah tombol Undo bisa ditekan"""
        return len(self.undo_stack) > 0

    def can_redo(self):
        """Metode helper untuk UI: Mengecek apakah tombol Redo bisa ditekan"""
        return len(self.redo_stack) > 0

    def clear_history(self):
        """
        Panggil ini saat user menekan fitur 'New File' atau 'Load JSON'.
        Ini akan menghapus semua memori agar kanvas benar-benar bersih.
        """
        self.undo_stack.clear()
        self.redo_stack.clear()
        print("[Riwayat] Memori dikosongkan.")