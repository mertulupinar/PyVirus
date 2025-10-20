"""
PyVirus - Oxynos Antivirus Scanner Pro
Unit Test Dosyası

Created by Oxynos
"""

import unittest
import os
import json
import tempfile
import shutil
from pathlib import Path

# Test için modülü import et
import sys
sys.path.insert(0, os.path.dirname(__file__))

from PyVirüs import (
    calculate_hash,
    load_virus_signatures,
    save_virus_signatures,
    update_virus_signatures,
    remove_virus_signature,
    scan_file,
    move_to_quarantine,
    VIRUS_DB_FILE,
    QUARANTINE_FOLDER
)


class TestHashCalculation(unittest.TestCase):
    """Hash hesaplama testleri."""
    
    def setUp(self):
        """Test için geçici dosya oluştur."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp_file.write("Test içeriği")
        self.temp_file.close()
    
    def tearDown(self):
        """Test dosyasını sil."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_md5_hash(self):
        """MD5 hash hesaplama testi."""
        hash_value = calculate_hash(self.temp_file.name, algorithm='md5')
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 32)  # MD5 32 karakter
    
    def test_sha256_hash(self):
        """SHA256 hash hesaplama testi."""
        hash_value = calculate_hash(self.temp_file.name, algorithm='sha256')
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)  # SHA256 64 karakter
    
    def test_nonexistent_file(self):
        """Var olmayan dosya için hash testi."""
        hash_value = calculate_hash("nonexistent_file.txt")
        self.assertIsNone(hash_value)


class TestVirusSignatures(unittest.TestCase):
    """Virus imza yönetimi testleri."""
    
    def setUp(self):
        """Test için yedek oluştur."""
        self.backup_file = None
        if os.path.exists(VIRUS_DB_FILE):
            self.backup_file = VIRUS_DB_FILE + ".backup"
            shutil.copy(VIRUS_DB_FILE, self.backup_file)
    
    def tearDown(self):
        """Yedeği geri yükle."""
        if self.backup_file and os.path.exists(self.backup_file):
            shutil.move(self.backup_file, VIRUS_DB_FILE)
        elif os.path.exists(VIRUS_DB_FILE):
            os.remove(VIRUS_DB_FILE)
    
    def test_save_and_load_signatures(self):
        """İmza kaydetme ve yükleme testi."""
        test_signatures = {"hash1", "hash2", "hash3"}
        save_virus_signatures(test_signatures)
        
        loaded_signatures = load_virus_signatures()
        self.assertEqual(test_signatures, loaded_signatures)
    
    def test_update_signatures(self):
        """İmza güncelleme testi."""
        initial_signatures = {"hash1", "hash2"}
        save_virus_signatures(initial_signatures)
        
        new_signatures = {"hash3", "hash4"}
        update_virus_signatures(new_signatures)
        
        all_signatures = load_virus_signatures()
        self.assertEqual(len(all_signatures), 4)
        self.assertTrue("hash1" in all_signatures)
        self.assertTrue("hash3" in all_signatures)
    
    def test_remove_signature(self):
        """İmza silme testi."""
        test_signatures = {"hash1", "hash2", "hash3"}
        save_virus_signatures(test_signatures)
        
        result = remove_virus_signature("hash2")
        self.assertTrue(result)
        
        remaining = load_virus_signatures()
        self.assertEqual(len(remaining), 2)
        self.assertFalse("hash2" in remaining)
    
    def test_remove_nonexistent_signature(self):
        """Var olmayan imza silme testi."""
        test_signatures = {"hash1", "hash2"}
        save_virus_signatures(test_signatures)
        
        result = remove_virus_signature("hash999")
        self.assertFalse(result)


class TestFileScan(unittest.TestCase):
    """Dosya tarama testleri."""
    
    def setUp(self):
        """Test dosyaları oluştur."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp_file.write("Temiz dosya içeriği")
        self.temp_file.close()
        
        self.file_hash = calculate_hash(self.temp_file.name)
    
    def tearDown(self):
        """Test dosyasını sil."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_scan_clean_file(self):
        """Temiz dosya tarama testi."""
        virus_sigs = {"different_hash_123"}
        path, is_virus = scan_file(self.temp_file.name, virus_sigs)
        
        self.assertEqual(path, self.temp_file.name)
        self.assertFalse(is_virus)
    
    def test_scan_infected_file(self):
        """Virüslü dosya tarama testi."""
        virus_sigs = {self.file_hash}
        path, is_virus = scan_file(self.temp_file.name, virus_sigs)
        
        self.assertEqual(path, self.temp_file.name)
        self.assertTrue(is_virus)


class TestQuarantine(unittest.TestCase):
    """Karantina testleri."""
    
    def setUp(self):
        """Test dosyası oluştur."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp_file.write("Virüslü dosya içeriği")
        self.temp_file.close()
    
    def tearDown(self):
        """Karantina klasörünü temizle."""
        if os.path.exists(QUARANTINE_FOLDER):
            shutil.rmtree(QUARANTINE_FOLDER)
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_move_to_quarantine(self):
        """Karantinaya taşıma testi."""
        original_path = self.temp_file.name
        
        quarantine_path = move_to_quarantine(original_path)
        
        # Orijinal dosya artık yok
        self.assertFalse(os.path.exists(original_path))
        
        # Karantina dosyası var
        self.assertTrue(os.path.exists(quarantine_path))
        self.assertTrue(quarantine_path.startswith(QUARANTINE_FOLDER))


class TestPerformance(unittest.TestCase):
    """Performans testleri."""
    
    def test_cache_performance(self):
        """Cache mekanizması performans testi."""
        import time
        
        # Test imzaları oluştur
        large_signatures = {f"hash_{i}" for i in range(10000)}
        save_virus_signatures(large_signatures)
        
        # İlk yükleme
        start = time.time()
        sigs1 = load_virus_signatures()
        first_load_time = time.time() - start
        
        # Cache'den yükleme
        start = time.time()
        sigs2 = load_virus_signatures()
        cached_load_time = time.time() - start
        
        # Cache çok daha hızlı olmalı
        self.assertLess(cached_load_time, first_load_time / 10)
        self.assertEqual(len(sigs1), len(sigs2))
        
        # Temizlik
        if os.path.exists(VIRUS_DB_FILE):
            os.remove(VIRUS_DB_FILE)


def run_tests():
    """Tüm testleri çalıştır."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestHashCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestVirusSignatures))
    suite.addTests(loader.loadTestsFromTestCase(TestFileScan))
    suite.addTests(loader.loadTestsFromTestCase(TestQuarantine))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("=" * 70)
    print("PyVirus - Oxynos Antivirus Scanner Pro")
    print("Unit Test Suite")
    print("Created by Oxynos")
    print("=" * 70)
    print()
    
    result = run_tests()
    
    print()
    print("=" * 70)
    print(f"Testler tamamlandı: {result.testsRun} test çalıştırıldı")
    print(f"Başarılı: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Başarısız: {len(result.failures)}")
    print(f"Hata: {len(result.errors)}")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)

