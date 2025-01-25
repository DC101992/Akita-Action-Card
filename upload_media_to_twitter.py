def upload_media_to_twitter(image_data):
    """Upload media to Twitter and return the media ID."""
    try:
        media_url = "https://upload.twitter.com/1.1/media/upload.json"
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
        }

        # Save the image locally for upload
        with open("temp_image.jpg", "wb") as temp_file:
            temp_file.write(image_data.getbuffer())

        with open("temp_image.jpg", "rb") as media_file:
            files = {"media": media_file}
            response = requests.post(media_url, headers=headers, files=files)

        os.remove("temp_image.jpg")  # Clean up temporary file

        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            media_id = response.json().get("media_id_string")
            print(f"Media uploaded successfully. Media ID: {media_id}")
            return media_id
        else:
            print(f"Media upload failed: {response.json()}")
            return None
    except Exception as e:
        print(f"Error uploading media: {e}")
        return None
