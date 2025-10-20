"""
PyVirus - Oxynos Antivirus Scanner Pro
Bulut Tabanlı İmza Güncelleme Modülü

Created by Oxynos
"""

import os
import json
import logging
import hashlib
from typing import Set, Optional
from datetime import datetime
from urllib import request, error

logger = logging.getLogger('OxynosAV.CloudUpdater')

# Bulut güncelleme ayarları
CLOUD_UPDATE_URL = "https://raw.githubusercontent.com/example/virus-signatures/main/signatures.json"
LOCAL_CACHE_FILE = "cloud_signatures_cache.json"
UPDATE_INTERVAL = 3600  # 1 saat (saniye cinsinden)


class CloudUpdater:
    """Bulut tabanlı virus imzası güncelleme sınıfı."""
    
    def __init__(self, update_url: str = CLOUD_UPDATE_URL):
        self.update_url = update_url
        self.cache_file = LOCAL_CACHE_FILE
        self.last_update = self._load_last_update_time()
    
    def _load_last_update_time(self) -> float:
        """Son güncelleme zamanını yükle."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('last_update', 0)
            except Exception as e:
                logger.warning(f"Cache dosyası okunamadı: {e}")
        return 0
    
    def _save_update_time(self, timestamp: float):
        """Son güncelleme zamanını kaydet."""
        try:
            data = {'last_update': timestamp, 'date': datetime.fromtimestamp(timestamp).isoformat()}
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Cache zamanı kaydedilemedi: {e}")
    
    def check_for_updates(self) -> bool:
        """Güncelleme gerekli mi kontrol et."""
        current_time = datetime.now().timestamp()
        time_since_last_update = current_time - self.last_update
        
        if time_since_last_update < UPDATE_INTERVAL:
            logger.info(f"Güncelleme gerekli değil. Son güncelleme: {int(time_since_last_update)}s önce")
            return False
        
        logger.info("Güncelleme kontrolü yapılıyor...")
        return True
    
    def fetch_cloud_signatures(self, timeout: int = 10) -> Optional[Set[str]]:
        """
        Buluttan virus imzalarını indir.
        
        Args:
            timeout: İstek zaman aşımı (saniye)
        
        Returns:
            İmza seti veya None (hata durumunda)
        """
        try:
            logger.info(f"Buluttan imzalar indiriliyor: {self.update_url}")
            
            req = request.Request(
                self.update_url,
                headers={'User-Agent': 'OxynosAV/1.0'}
            )
            
            with request.urlopen(req, timeout=timeout) as response:
                data = response.read().decode('utf-8')
                signatures = json.loads(data)
                
                if isinstance(signatures, list):
                    signature_set = set(signatures)
                    logger.info(f"Buluttan {len(signature_set)} imza indirildi")
                    return signature_set
                else:
                    logger.error("Geçersiz imza formatı (liste bekleniyor)")
                    return None
        
        except error.URLError as e:
            logger.error(f"Ağ hatası: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse hatası: {e}")
            return None
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return None
    
    def merge_signatures(self, local_sigs: Set[str], cloud_sigs: Set[str]) -> Set[str]:
        """
        Yerel ve bulut imzalarını birleştir.
        
        Args:
            local_sigs: Yerel imzalar
            cloud_sigs: Bulut imzalar
        
        Returns:
            Birleştirilmiş imza seti
        """
        merged = local_sigs.union(cloud_sigs)
        new_count = len(merged) - len(local_sigs)
        
        if new_count > 0:
            logger.info(f"{new_count} yeni imza eklendi (Toplam: {len(merged)})")
        else:
            logger.info("Yeni imza eklenmedi, veritabanı güncel")
        
        return merged
    
    def update_from_cloud(self, local_signatures: Set[str]) -> Optional[Set[str]]:
        """
        Buluttan güncelleme yap.
        
        Args:
            local_signatures: Mevcut yerel imzalar
        
        Returns:
            Güncellenmiş imza seti veya None (güncelleme başarısızsa)
        """
        if not self.check_for_updates():
            return None
        
        cloud_sigs = self.fetch_cloud_signatures()
        
        if cloud_sigs is None:
            logger.warning("Bulut güncellemesi başarısız")
            return None
        
        merged_sigs = self.merge_signatures(local_signatures, cloud_sigs)
        
        # Güncelleme zamanını kaydet
        self._save_update_time(datetime.now().timestamp())
        
        return merged_sigs
    
    def force_update(self, local_signatures: Set[str]) -> Optional[Set[str]]:
        """
        Zorla güncelleme yap (zaman kontrolü yapmadan).
        
        Args:
            local_signatures: Mevcut yerel imzalar
        
        Returns:
            Güncellenmiş imza seti veya None
        """
        logger.info("Zorla güncelleme başlatıldı")
        self.last_update = 0  # Zaman kontrolünü devre dışı bırak
        return self.update_from_cloud(local_signatures)


# Test ve demo fonksiyonu
def demo_update():
    """Demo güncelleme işlemi."""
    print("=" * 70)
    print("PyVirus - Cloud Updater Demo")
    print("Created by Oxynos")
    print("=" * 70)
    print()
    
    # Örnek yerel imzalar
    local_sigs = {
        "a5574ac5b29885fe6632de1007bc74ac",
        "a55302ad4bf2f050513528a2ca64ff01",
        "a54a9d3da9465c3861fea4c9985600ab"
    }
    
    print(f"Yerel imza sayısı: {len(local_sigs)}")
    print()
    
    # Updater oluştur
    updater = CloudUpdater()
    
    # Güncelleme kontrolü
    print("Güncelleme kontrol ediliyor...")
    if updater.check_for_updates():
        print("✓ Güncelleme mevcut")
        
        # Not: Gerçek URL olmadığı için başarısız olacak
        print("(Demo: Gerçek URL konfigüre edilmeli)")
    else:
        print("✓ Veritabanı güncel")
    
    print()
    print("=" * 70)
    print("Not: Gerçek kullanım için CLOUD_UPDATE_URL değişkenini")
    print("     geçerli bir JSON endpoint'e ayarlayın.")
    print("=" * 70)


if __name__ == '__main__':
    # Demo çalıştır
    demo_update()

