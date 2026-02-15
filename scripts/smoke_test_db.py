import os
from db.valkey_store import ValkeyStore

store = ValkeyStore(
    host=os.getenv("VALKEY_HOST", "127.0.0.1"),
    port=int(os.getenv("VALKEY_PORT", "6379")),
)

t = store.get_tenant_by_api_key(os.getenv("CATPHISH_API_KEY", "demo_key_123"))
print("tenant:", t)

u = store.upsert_user_embedding("t_demo", "user_999", [1,2,3])
print("user:", u)

ch = store.create_challenge("t_demo", "ch_test", "user_999", "Unique New York", ttl_seconds=60)
print("challenge:", ch)

print("lock1:", store.claim_challenge_lock("t_demo", "ch_test"))
print("lock2:", store.claim_challenge_lock("t_demo", "ch_test"))

