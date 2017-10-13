import os
import requests
import simplejson as json
import os.path as op
from nipype.utils.filemanip import load_json, save_json
import hashlib
import numpy as np
import tempfile
assert os.environ["ZENODO_TOKEN"], "Please have a system variable ZENODO_TOKEN defined"

ACCESS_TOKEN = os.environ["ZENODO_TOKEN"]

def get_depositions():
    r = requests.get('https://zenodo.org/api/deposit/depositions',
                     params={'access_token': ACCESS_TOKEN})
    assert r.status_code == 200, r.json()
    return r.json()

def create_empty_deposition():
    headers = {"Content-Type": "application/json"}
    r = requests.post('https://zenodo.org/api/deposit/depositions',
                      params={'access_token': ACCESS_TOKEN}, json={},
                  headers=headers)
    assert r.status_code == 201, r.json()
    return r.json()

def upload_file_to_deposition(deposition_id, filename):
    # Get the deposition id from the previous response

    data = {'filename': filename}
    files = {'file': open(filename, 'rb')}
    r = requests.post('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                      params={'access_token': ACCESS_TOKEN}, data=data,
                      files=files)
    assert r.status_code == 201, r.json()
    return r.json()

def upload_large_file_to_deposition(bucket_url, filename):
    r = requests.put('%s/%s' % (bucket_url,filename),
                data=open(filename, 'rb'),
                headers={"Accept":"application/json",
                "Authorization":"Bearer %s" % ACCESS_TOKEN,
                "Content-Type":"application/octet-stream"})

    print("uploaded large file", r.status_code)
    return r.json()

def create_deposition_metadata(title, upload_type, description, creators):
    """
    creators = [{'name': 'Doe, John',
                  'affiliation': 'Zenodo'}]
    """
    return {'title': title,
            'upload_type': upload_type,
            'description': description,
            'creators': creators
            }

def update_deposition_metadata(deposition_id, metadata):
    data = {'metadata': metadata}
    headers = {"Content-Type": "application/json"}

    r = requests.put('https://zenodo.org/api/deposit/depositions/%s' % deposition_id,
                     params={'access_token': ACCESS_TOKEN}, data=json.dumps(data),
                     headers=headers)
    assert r.status_code == 200, r.json()
    return r.json()

def get_deposition_files(deposition_id):
    import requests
    r = requests.get('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                 params={'access_token': ACCESS_TOKEN})
    assert r.status_code == 200, r.json()
    return r.json()

def get_data_manifest_deposition():
    zenodo_deps = get_depositions()
    for dep in zenodo_deps:
        if dep["title"] == "Data Manifest":
            return dep
    raise FileNotFoundError("Please create a manifest deposition. See examples/create_data_manifest.py")


def safe_upload_to_deposition(data_file, title, description, creators):
    manifest = get_data_manifest_deposition()

    m = hashlib.md5()
    data = np.load(data_file)

    for value in data:
        m.update(str(value).encode("utf-8"))

    new_manifest_hash = m.hexdigest()
    new_manifest_data = {}

    #check filenames in manifest
    manifest_files = get_deposition_files(manifest["id"])
    manifest_filenames = [mf["filename"] for mf in manifest_files]

    assert new_manifest_hash+".json" not in manifest_filenames, "This data already exists!"

    # upload the file to a new deposition

    new_dep = create_empty_deposition()
    metadata = create_deposition_metadata(title,
        "dataset",
        description + " md5-data-hash: %s" %new_manifest_hash,
        creators)
    update_deposition_metadata(new_dep["id"], metadata)
    print("Going to upload large file ...")
    upload_large_file_to_deposition(new_dep["links"]["bucket"], data_file)

    # record that deposition to the manifest data

    new_manifest_data["metadata"] = metadata
    new_manifest_data["md5_hash"] = new_manifest_hash
    new_manifest_data["deposition"] = new_dep
    manifest_save_dir = tempfile.mkdtemp()
    manifest_filename = op.join(manifest_save_dir, new_manifest_hash+".json")
    save_json(manifest_filename, new_manifest_data)
    print("Going to update the data manifest ...")
    # save that to the manifest deposition
    upload_file_to_deposition(manifest["id"], manifest_filename)
    print("Done with all uploads")
    return new_dep
