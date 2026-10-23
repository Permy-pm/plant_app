import base64

def get_base64_image(image_path):
    """
    Gets the base64 encoded string of an image file.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error encoding image: {e}")
        return ""