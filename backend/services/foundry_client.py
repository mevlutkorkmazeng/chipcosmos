"""Foundry Local yönetici singleton'ı.

rag.py'deki get_manager()/get_model() ile aynı mimari: hello_model.py'den
beri kullanılan Configuration/FoundryLocalManager kurulum deseni.
"""

from foundry_local_sdk import Configuration, FoundryLocalManager

_manager: FoundryLocalManager | None = None


def get_manager() -> FoundryLocalManager:
    global _manager
    if _manager is None:
        FoundryLocalManager.initialize(Configuration(app_name="local-rag-assistant"))
        _manager = FoundryLocalManager.instance
    return _manager


def get_model(manager: FoundryLocalManager, alias: str, task_hint: str):
    """Katalogdan verilen alias'ı bulur; yoksa aynı görev için mevcut ilk modele düşer."""
    model = manager.catalog.get_model(alias)
    if model is not None:
        return model

    for candidate in manager.catalog.list_models():
        if candidate.info.task == task_hint:
            return candidate

    raise RuntimeError(f"Katalogda '{task_hint}' görevi için model bulunamadı.")


def get_embedding_client(manager: FoundryLocalManager, alias: str):
    model = get_model(manager, alias, "embeddings")
    model.download()
    model.load()
    return model.get_embedding_client()


def get_chat_client(manager: FoundryLocalManager, alias: str, max_tokens: int):
    model = get_model(manager, alias, "chat-completion")
    model.download()
    model.load()
    client = model.get_chat_client()
    client.settings.max_tokens = max_tokens
    return client
