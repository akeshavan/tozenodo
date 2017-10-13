import os
import requests
import simplejson as json

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
    deposition_id = r.json()['id']
    data = {'filename': filename}
    files = {'file': open(filename, 'rb')}
    r = requests.post('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                      params={'access_token': ACCESS_TOKEN}, data=data,
                      files=files)
    assert r.status_code == 201, r.json()
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

def get_data_manifest_deposition():
    zenodo_deps = tz.get_depositions()
    for dep in zenodo_deps:
        if dep["title"] == "Data Manifest":
            return dep
    raise FileNotFoundError("Please create a manifest deposition. See examples/create_data_manifest.py")
