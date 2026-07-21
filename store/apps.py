from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    verbose_name = 'Shop'

    def ready(self):
        _patch_file_locks_if_unsupported()


def _patch_file_locks_if_unsupported():
    """
    Django's default file storage takes an OS-level lock (flock) while
    saving each uploaded/downloaded file. Some filesystems don't support
    this — notably Android's shared/external storage, which is what apps
    like Pydroid3 and Termux use when a project lives under
    /storage/emulated/0/... . There, every file save fails with:
        OSError: [Errno 38] Function not implemented

    This probes whether locking actually works inside MEDIA_ROOT at
    startup, and if it doesn't, disables locking so file saves succeed.
    On a normal server/filesystem where locking works fine, this is a
    no-op and nothing changes.
    """
    import os

    from django.conf import settings
    from django.core.files import locks

    media_root = str(settings.MEDIA_ROOT)
    try:
        os.makedirs(media_root, exist_ok=True)
        probe_path = os.path.join(media_root, '.lock_probe')
        with open(probe_path, 'wb') as f:
            locks.lock(f, locks.LOCK_EX)
            locks.unlock(f)
        os.remove(probe_path)
    except OSError:
        locks.lock = lambda f, flags: True
        locks.unlock = lambda f: True
