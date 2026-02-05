# external/memory_repos.py
from capabilities.llm_memory.unified_manageer.memory_interfaces import (
    IVaultRepository,
    IProceduralRepository,
    IResourceRepository,
)
from env import MEMORY_CONFIG  # ← 从系统统一配置读取
# ========================
# 工厂函数
# ========================
def build_vault_repo() -> IVaultRepository:
    config = MEMORY_CONFIG["vault"]
    from .sqLite_vault_dao import SQLiteVaultDAO
    from .security import Encryptor
    from .encrypte_vault_repository import EncryptedVaultRepository

    dao = SQLiteVaultDAO(config["db_path"])
    encryptor = Encryptor(config.get("encryption_key_b64"))
    return EncryptedVaultRepository(dao, encryptor)

def build_procedural_repo() -> IProceduralRepository:
    config = MEMORY_CONFIG["procedural"]
    from .filebased_procedural_repository import FileBasedProceduralRepository

    return FileBasedProceduralRepository(config["dir"])

def build_resource_repo() -> IResourceRepository:
    config = MEMORY_CONFIG["resource"]
    from .sqlite_resource_dao import SQLiteResourceDAO
    from .storage import get_minio_client  # ← 统一获取 MinIO 客户端
    from .resource_repository import ResourceRepository

    dao = SQLiteResourceDAO(config["db_path"])
    minio_client = get_minio_client() if config.get("use_minio") else None
    return ResourceRepository(
        dao=dao,
        use_minio=config.get("use_minio", False),
        minio_client=minio_client,
        local_dir=config.get("local_dir"),
    )
