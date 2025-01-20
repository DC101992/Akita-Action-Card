
from PIL import Image

# Define the path to your image
image_path = r'C:\Users\taggm\OneDrive\Desktop\akita action card\akita action card.jpg'

# Open the image
img = Image.open(image_path)

# Display the image in the default viewer
img.show()

# If you'd like to save it after modifications, you can do so:
# img.save('new_image.jpg')


