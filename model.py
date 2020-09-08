import kfserving
from typing import List, Dict
from PIL import Image
import base64
import io
import logging
import SimpleITK as sitk
import numpy as np
import requests, json
import sys, os
import rpy2.robjects as robjects

model_name = 'custom_r'
#model_name = os.getenv('MODEL_NAME',None)
IN_DIR = ""

class KFServingSampleModel(kfserving.KFModel):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

    def load(self):
        self.ready = True

    def predict(self, inputs: Dict) -> Dict:
        del inputs['instances']
        logging.info("prep =======> %s",str(type(inputs)))
        try:
            json_data = inputs
        except ValueError:
            return json.dumps({ "error": "Recieved invalid json" })
        with open('model.R','r') as f:
            rstring = f.read()
        rfunc=robjects.r(rstring)
        preds = rfunc(IN_DIR)
        preds = np.asarray(preds)
        return {"predictions:":preds.tolist()}

if __name__ == "__main__":
    model = KFServingSampleModel(model_name)
    model.load()
    kfserving.KFServer(workers=1).start([model])