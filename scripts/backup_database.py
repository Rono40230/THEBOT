from src.thebot.core.logger import logger
#!/usr/bin/env python3
"""
Script de sauvegarde automatique de base de données - Phase 5
Supporte SQLite et PostgreSQL avec rotation et compression
"""

import os
import sys
import time
import gzip
import shutil
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Classe pour gérer les sauvegardes de base de données"""
    
    def __init__(self, config_file: str = "backup_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.backup_dir = Path(self.config.get("backup_dir", "./backups"))
        self.backup_dir.mkdir(exist_ok=True)
        
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier JSON"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Configuration par défaut
            return {
                "database_type": "sqlite",
                "database_path": "./data/thebot.db",
                "backup_dir": "./backups",
                "max_backups": 30,
                "compress": True,
                "schedule": "daily"
            }
    
    def _save_config(self) -> None:
        """Sauvegarde la configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def backup_sqlite(self) -> bool:
        """Effectue une sauvegarde SQLite"""
        db_path = Path(self.config["database_path"])
        if not db_path.exists():
            logger.warning(f"Base de données non trouvée: {db_path}")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"thebot_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Copie simple pour SQLite (puisque c'est un fichier unique)
            shutil.copy2(db_path, backup_path)
            logger.info(f"✅ Sauvegarde SQLite créée: {backup_path}")
            
            # Compression si activée
            if self.config.get("compress", True):
                self._compress_file(backup_path)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde SQLite: {e}")
            return False
    
    def backup_postgresql(self) -> bool:
        """Effectue une sauvegarde PostgreSQL"""
        try:
            import subprocess
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"thebot_postgres_backup_{timestamp}.sql"
            backup_path = self.backup_dir / backup_name
            
            # Commande pg_dump
            cmd = [
                "pg_dump",
                "--host", self.config.get("pg_host", "localhost"),
                "--port", str(self.config.get("pg_port", 5432)),
                "--username", self.config.get("pg_user", "thebot"),
                "--dbname", self.config.get("pg_database", "thebot"),
                "--no-password",
                "--format", "c",  # Format custom
                "--compress", "9",
                "--file", str(backup_path)
            ]
            
            # Variables d'environnement pour le mot de passe
            env = os.environ.copy()
            if "pg_password" in self.config:
                env["PGPASSWORD"] = self.config["pg_password"]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Sauvegarde PostgreSQL créée: {backup_path}")
                return True
            else:
                logger.error(f"❌ Erreur pg_dump: {result.stderr}")
                return False
                
        except ImportError:
            logger.error("❌ pg_dump non disponible. Installez PostgreSQL client tools.")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde PostgreSQL: {e}")
            return False
    
    def _compress_file(self, file_path: Path) -> None:
        """Compresse un fichier avec gzip"""
        compressed_path = file_path.with_suffix(file_path.suffix + ".gz")
        
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Supprimer le fichier original
            file_path.unlink()
            logger.info(f"🗜️ Fichier compressé: {compressed_path}")
            
        except Exception as e:
            logger.error(f"❌ Erreur compression: {e}")
    
    def cleanup_old_backups(self) -> None:
        """Nettoie les anciennes sauvegardes selon la politique de rétention"""
        max_backups = self.config.get("max_backups", 30)
        
        # Lister tous les fichiers de sauvegarde
        backup_files = list(self.backup_dir.glob("thebot_backup_*"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Supprimer les anciens
        if len(backup_files) > max_backups:
            to_delete = backup_files[max_backups:]
            for old_file in to_delete:
                old_file.unlink()
                logger.info(f"🗑️ Ancienne sauvegarde supprimée: {old_file}")
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des sauvegardes"""
        backup_files = list(self.backup_dir.glob("thebot_backup_*"))
        
        total_size = sum(f.stat().st_size for f in backup_files)
        oldest_backup = None
        newest_backup = None
        
        if backup_files:
            backup_files.sort(key=lambda x: x.stat().st_mtime)
            oldest_backup = datetime.fromtimestamp(backup_files[0].stat().st_mtime)
            newest_backup = datetime.fromtimestamp(backup_files[-1].stat().st_mtime)
        
        return {
            "total_backups": len(backup_files),
            "total_size_mb": total_size / (1024 * 1024),
            "oldest_backup": oldest_backup.isoformat() if oldest_backup else None,
            "newest_backup": newest_backup.isoformat() if newest_backup else None,
            "backup_dir": str(self.backup_dir)
        }
    
    def run_backup(self) -> bool:
        """Exécute une sauvegarde complète"""
        logger.info("🚀 Démarrage de la sauvegarde...")
        start_time = time.time()
        
        db_type = self.config.get("database_type", "sqlite")
        
        if db_type == "sqlite":
            success = self.backup_sqlite()
        elif db_type == "postgresql":
            success = self.backup_postgresql()
        else:
            logger.error(f"❌ Type de base non supporté: {db_type}")
            return False
        
        if success:
            # Nettoyer les anciennes sauvegardes
            self.cleanup_old_backups()
            
            # Statistiques
            stats = self.get_backup_stats()
            duration = time.time() - start_time
            
            logger.info(f"✅ Sauvegarde terminée en {duration:.2f}s")
            logger.info(f"📊 Statistiques: {stats['total_backups']} sauvegardes, {stats['total_size_mb']:.1f}MB")
            
            return True
        else:
            logger.error("❌ Échec de la sauvegarde")
            return False


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Sauvegarde automatique de base de données THEBOT")
    parser.add_argument("--config", default="backup_config.json", help="Fichier de configuration")
    parser.add_argument("--type", choices=["sqlite", "postgresql"], help="Type de base de données")
    parser.add_argument("--run", action="store_true", help="Exécuter la sauvegarde")
    parser.add_argument("--stats", action="store_true", help="Afficher les statistiques")
    parser.add_argument("--setup", action="store_true", help="Configurer la sauvegarde")
    
    args = parser.parse_args()
    
    try:
        backup = DatabaseBackup(args.config)
        
        if args.setup:
            # Configuration interactive
            logger.info("🔧 Configuration de la sauvegarde")
            
            db_type = input(f"Type de base (sqlite/postgresql) [{backup.config['database_type']}]: ").strip()
            if db_type:
                backup.config["database_type"] = db_type
            
            if db_type == "sqlite":
                db_path = input(f"Chemin de la base SQLite [{backup.config['database_path']}]: ").strip()
                if db_path:
                    backup.config["database_path"] = db_path
            elif db_type == "postgresql":
                backup.config["pg_host"] = input(f"Host PostgreSQL [{backup.config.get('pg_host', 'localhost')}]: ").strip() or "localhost"
                backup.config["pg_port"] = int(input(f"Port PostgreSQL [{backup.config.get('pg_port', 5432)}]: ").strip() or 5432)
                backup.config["pg_user"] = input(f"Utilisateur PostgreSQL [{backup.config.get('pg_user', 'thebot')}]: ").strip() or "thebot"
                backup.config["pg_database"] = input(f"Base de données [{backup.config.get('pg_database', 'thebot')}]: ").strip() or "thebot"
                backup.config["pg_password"] = input("Mot de passe PostgreSQL: ").strip()
            
            backup_dir = input(f"Répertoire de sauvegarde [{backup.config['backup_dir']}]: ").strip()
            if backup_dir:
                backup.config["backup_dir"] = backup_dir
            
            max_backups = input(f"Nombre maximum de sauvegardes [{backup.config['max_backups']}]: ").strip()
            if max_backups:
                backup.config["max_backups"] = int(max_backups)
            
            backup._save_config()
            logger.info("✅ Configuration sauvegardée")
            
        elif args.stats:
            # Afficher les statistiques
            stats = backup.get_backup_stats()
            logger.info("📊 Statistiques des sauvegardes:")
            logger.info(f"  Total: {stats['total_backups']} sauvegardes")
            logger.info(f"  Taille: {stats['total_size_mb']:.1f}MB")
            logger.info(f"  Plus ancienne: {stats['oldest_backup'] or 'Aucune'}")
            logger.info(f"  Plus récente: {stats['newest_backup'] or 'Aucune'}")
            logger.info(f"  Répertoire: {stats['backup_dir']}")
            
        elif args.run:
            # Exécuter la sauvegarde
            success = backup.run_backup()
            sys.exit(0 if success else 1)
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ Opération annulée")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
