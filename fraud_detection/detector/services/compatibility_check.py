import os
import dotenv

dotenv.load_dotenv()

_VERSION_TAG = os.environ.get('VERSION_TAG')
MAJOR_TAG_VERSION = _VERSION_TAG.split('.')[0] if _VERSION_TAG else None


def is_sw_up_to_date(latest_model_version: str) -> bool:
    ''' Checks if the software version is later or equal to the model version '''

    # Defaults to True if tag not set
    if not _VERSION_TAG:
        return True

    # False if None model version
    if not latest_model_version:
        print("WARN - Model version is None")
        return False

    # Return true if model version is newer
    major_model_version = latest_model_version.split('.')[0][1:]
    return int(MAJOR_TAG_VERSION) >= int(major_model_version)


def is_same_model_and_sw_version(model_version: str) -> bool:
    ''' Checks if the model version same as the software version '''

    # Defaults to True if tag not set
    if not _VERSION_TAG:
        return True

    # False if None model version
    if not model_version:
        print("WARN - Model version is None")
        return False

    # Return true if same major version
    major_model_version = model_version.split('.')[0][1:]
    return major_model_version == MAJOR_TAG_VERSION
