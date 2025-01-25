def upload_media_to_twitter(image_data):
    """Upload media to Twitter and return the media ID."""
    try:
        url = "https://upload.twitter.com/1.1/media/upload.json"
        auth = OAuth1(
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_SECRET
        )

        # Save the image locally for upload
        with open("temp_image.jpg", "wb") as temp_file:
            temp_file.write(image_data.getbuffer())

        with open("temp_image.jpg", "rb") as media_file:
            files = {"media": media_file}
            response = requests.post(url, auth=auth, files=files)

        os.remove("temp_image.jpg")  # Clean up temporary file

        if response.status_code == 200:
            media_id = response.json().get("media_id_string")
            print(f"Media uploaded successfully. Media ID: {media_id}")
            return media_id
        elif response.status_code == 401:
            print("Unauthorized. Please check your authentication credentials.")
        elif response.status_code == 403:
            print("Access to this API URL is forbidden. Check app permissions.")
        else:
            print(f"Unexpected response: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Error uploading media: {e}")
        return None
