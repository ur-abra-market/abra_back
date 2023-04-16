import sys

MIN_VERSION = (3, 8)
CURRENT_VERSION = (sys.version_info.major, sys.version_info.minor)

if CURRENT_VERSION < MIN_VERSION:
    raise SystemError(
        "Your python {current_version} version not supported, minimal version is {min_version}".format(
            current_version=CURRENT_VERSION, min_version=MIN_VERSION
        ),
    )
