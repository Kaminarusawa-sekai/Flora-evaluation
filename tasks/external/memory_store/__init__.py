_LAZY_EXPORTS = {
    "EncryptedVaultRepository": (".encrypte_vault_repository", "EncryptedVaultRepository"),
    "FileBasedProceduralRepository": (".filebased_procedural_repository", "FileBasedProceduralRepository"),
    "ResourceRepository": (".resource_repository", "ResourceRepository"),
    "Encryptor": (".security", "Encryptor"),
    "SQLiteVaultDAO": (".sqLite_vault_dao", "SQLiteVaultDAO"),
    "SQLiteResourceDAO": (".sqlite_resource_dao", "SQLiteResourceDAO"),
    "STMRecordDAO": (".stm_dao", "STMRecordDAO"),
    "get_minio_client": (".storage", "get_minio_client"),
    "build_vault_repo": (".memory_repos", "build_vault_repo"),
    "build_procedural_repo": (".memory_repos", "build_procedural_repo"),
    "build_resource_repo": (".memory_repos", "build_resource_repo"),
}


def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        import importlib
        module_path, attr_name = _LAZY_EXPORTS[name]
        module = importlib.import_module(module_path, __name__)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = list(_LAZY_EXPORTS.keys())
