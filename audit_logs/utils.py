from .models import AuditLog


def create_audit_log(
    actor,
    action,
    resource_type,
    resource_id,
    request=None,
    metadata=None,
):
    ip_address = None

    if request:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.META.get("REMOTE_ADDR")

    return AuditLog.objects.create(
        actor=actor if actor and actor.is_authenticated else None,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        ip_address=ip_address,
        metadata=metadata or {},
    )