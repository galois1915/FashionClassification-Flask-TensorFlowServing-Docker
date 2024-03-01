from flask import Flask, render_template, request 
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import json
from PIL import Image, ImageOps
import requests


#from tensorflow_serving.apis.predict_pb2 import PredictRequest
#from tensorflow_serving.apis import prediction_service_pb2_grpc
#import tensorflow  as tf    
#import grpc

app = Flask(__name__)

class_names = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]


def TF_connection_prediction(image, through="RESTapi"):
    '''
    if through=="grcp":

        ### REQUEST
        request = PredictRequest()
        request.model_spec.name = "my_mnist_model"
        request.model_spec.signature_name = "serving_default"
        input_name = "input_1"
        request.inputs[input_name].CopyFrom(tf.make_tensor_proto(image.tolist()))

        ### SEND THE REQUEST TO THE SERVER
        channel = grpc.insecure_channel("localhost:8500") # gRPC API "communication"
        predict_service = prediction_service_pb2_grpc.PredictionServiceStub(channel) #  create gRPC service over this channel
        response = predict_service.Predict(request, timeout=10.0) # send the request
        print("connection with grcp")

        ### PREDICTION
        output_name = 'dense_2'
        output_proto = response.outputs[output_name]
        y_proba = tf.make_ndarray(output_proto)
        print(y_proba)

        return y_proba
    '''    
    if through=="RESTapi":
        request_json = json.dumps({
            "signature_name": "serving_default",
            "instances": image.tolist()
        })

        server_url = "http://172.18.0.2:8501/v1/models/my_mnist_model:predict"
        response = requests.post(server_url, data=request_json)
        response.raise_for_status()
        print("concection with REST API")
        response = response.json()
        y_proba = np.array(response["predictions"])

        return y_proba


## Connection with TensorFlow Serving
def predict_MNIST_model(image):
    image = image/255.

    y_proba = TF_connection_prediction(image)

    ### BARPLOT FROM PREDICTIONS
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(18,10))
    ax.bar(class_names,y_proba[0].round(2))
    plt.xticks(fontsize=18, rotation=45)

    return plt 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/MNISTfashion", methods=["GET", "POST"])
def MNIST_fashion():
    status = ""

    if request.method == 'POST':
        try :
            
            # SAVE IMG
            f = request.files['file']
            path_img = os.path.join("./static/images", f.filename)
            f.save(path_img)
            status = "Upload successful"
            
            # PREDICTION AND BARPLOT
            img = Image.open(path_img)
            img = ImageOps.invert(img) # change because Image.open revert the pixel
            img = np.array(img)
            plot = predict_MNIST_model(image=img)
            path_prediction = os.path.join("./static/images", f.filename.split(".")[0]+"-prediction.png")
            plot.savefig(path_prediction)

            return render_template("MNIST_fashion.html", status=status, path_img=path_img, path_prediction=path_prediction)
        
        except IsADirectoryError: # IsADirectoryError, FileNotFounError, IOError
            status = "Upload failed!"

    return render_template("MNIST_fashion.html", status=status)


if __name__=="__main__":
    app.run(debug=True)

# export FLASK_ENV=development
# export FLASK_APP=main.py
# flask run --host=0.0.0.0
# flask --ap main.py run --debug