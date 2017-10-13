import tozenodo as tz
import os.path as op
from nipype.utils.filemanip import load_json, save_json
import hashlib
import numpy as np
import tempfile

data_path = op.join(tz.__path__[0], "data")

data_file = op.join(data_path, "satra_meningioma_dataset_10-13-2017.npz")

tz.safe_upload_to_deposition(data_file, "satra meningioma dataset 10-13-17",
                            "The original satra datasets from the task meningioma_001 on Medulina.",
                            [{"name": "Keshavan, Anisha", "affiliation": "University of Washington"}] )
