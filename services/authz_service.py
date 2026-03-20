import os

import casbin


_ENFORCER = None


def get_enforcer():
    global _ENFORCER
    if _ENFORCER is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        model_path = os.path.join(base_dir, "casbin_model.conf")
        policy_path = os.path.join(base_dir, "casbin_policy.csv")
        _ENFORCER = casbin.Enforcer(model_path, policy_path)
    return _ENFORCER


def can(role: str, obj: str, act: str) -> bool:
    enforcer = get_enforcer()
    normalized_role = (role or "").strip().lower()
    return bool(enforcer.enforce(normalized_role, obj, act))
