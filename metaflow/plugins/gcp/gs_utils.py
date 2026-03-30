import sys

from metaflow.exception import MetaflowException, MetaflowInternalError
from metaflow.plugins.gcp.gs_exceptions import MetaflowGSPackageError

# Safe import of GCP exceptions
try:
    from google.cloud.exceptions import NotFound, Forbidden
except ImportError:
    NotFound = None
    Forbidden = None


def parse_gs_full_path(gs_uri):
    from urllib.parse import urlparse

    #  <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    scheme, netloc, path, _, _, _ = urlparse(gs_uri)
    assert scheme == "gs"
    assert netloc is not None

    bucket = netloc
    path = path.lstrip("/").rstrip("/")
    if path == "":
        path = None

    return bucket, path


def _check_and_init_gs_deps():
    try:
        from google.cloud import storage
        import google.auth
    except ImportError:
        raise MetaflowGSPackageError()

    if sys.version_info[:2] < (3, 7):
        raise MetaflowException(
            msg="Metaflow may only use Google Cloud Storage with Python 3.7 or newer"
        )


def check_gs_deps(func):
    """The decorated function checks GS dependencies (as needed for Google Cloud storage backend). This includes
    various GCP SDK packages, as well as a Python version of >=3.7
    """

    def _inner_func(*args, **kwargs):
        _check_and_init_gs_deps()
        return func(*args, **kwargs)

    return _inner_func


@check_gs_deps
def process_gs_exception(e):
    """
    Translate errors to Metaflow errors for standardized messaging. The intent is that all
    Google Cloud Storage integration logic should send errors to this function for
    translation.

    We explicitly EXCLUDE executor related errors here. See handle_executor_exceptions
    """
    if isinstance(e, MetaflowException):
        # Already a MetaflowException — no translation needed
        raise

    if isinstance(e, ImportError):
        # Unexpected ImportError — re-raise for visibility
        raise

    # Handle common GCP errors explicitly
    if NotFound and isinstance(e, NotFound):
        raise MetaflowInternalError(
            msg="GCS resource not found: %s" % str(e)
        )

    if Forbidden and isinstance(e, Forbidden):
        raise MetaflowInternalError(
            msg="Access denied to GCS resource: %s" % str(e)
        )

    # Fallback for all other errors
    raise MetaflowInternalError(msg=str(e))
