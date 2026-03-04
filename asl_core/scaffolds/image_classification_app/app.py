"""Streamlit Image Classification App"""

import numpy as np
import streamlit as st
import tensorflow as tf
from tensorflow.keras.models import load_model

st.set_page_config(page_title="5-Flower Classifier", page_icon="🌷")

st.title("5-Flower Classifier")

st.markdown(
    "Welcome to this simple web application that classifies 5 flowers"
    + "(daisy, dandelion, roses, sunflowers, tulips)."
)

IMG_HEIGHT = 224
IMG_WIDTH = 224
IMG_CHANNELS = 3
CLASSES = ["daisy", "dandelion", "roses", "sunflowers", "tulips"]


@st.cache_resource(show_spinner=False)
def load_and_cache_model():
    model_path = "flowers_model"
    model = load_model(model_path)
    return model


def read_image(img_bytes):
    img = tf.image.decode_jpeg(img_bytes, channels=IMG_CHANNELS)
    img = tf.image.convert_image_dtype(img, tf.float32)
    return img


def predict(model, image):
    image = tf.image.resize(image, [IMG_HEIGHT, IMG_WIDTH])
    image = np.expand_dims(image, axis=0)
    predictions = model.predict(image)
    pred_index = np.argmax(predictions[0])
    return predictions[0][pred_index], CLASSES[pred_index]


def main():
    file_uploaded = st.file_uploader("Choose File", type=["png", "jpg", "jpeg"])
    if file_uploaded is not None:
        image = read_image(file_uploaded.read())
        st.image(image.numpy(), caption="Uploaded Image", use_column_width=True)
        class_btn = st.button("Classify")
        if class_btn:
            with st.spinner("Model predicting...."):
                loaded_model = load_and_cache_model()
                prob, prediction = predict(loaded_model, image)
                st.success(f"Prediction: {prediction} - {prob:.2%}")


if __name__ == "__main__":
    main()
