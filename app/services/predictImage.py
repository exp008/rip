import os
import onnxruntime
import numpy as np
from PIL import Image


imageClassList = {'0': 'Нефтедобыча', '1': 'Продукты питания', '2': 'Строительство'}  #Сюда указать классы

def predictImageData(image):
    img = Image.open(image).convert("RGB")
    img = np.asarray(img.resize((32, 32), Image.LANCZOS))
    sess = onnxruntime.InferenceSession(os.getcwd() + '/app/static/models/cifar100.onnx') #<-Здесь требуется указать свой путь к модели
    outputOFModel = np.argmax(sess.run(None, {'input': np.asarray([img]).astype(np.float32)}))
    score = imageClassList[str(outputOFModel)]
    return score