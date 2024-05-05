import io
import re
import streamlit as st
from pytube import YouTube, exceptions as pytube_exceptions


def sanitize_filename(filename):
    """Sanitize filename by removing or replacing invalid characters for Windows filesystems."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)


def get_highest_resolution(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if stream:
            return stream.resolution
        else:
            st.error("No suitable video streams found.")
            return None
    except pytube_exceptions.AgeRestrictedError:
        st.error(
            "This video is age-restricted and requires login to access. This tool does not support downloading "
            "age-restricted content.")
        return None
    except pytube_exceptions.PytubeError as e:
        st.error(f"Error accessing video streams: {str(e)}")
        return None


def download_video(url, resolution):
    with st.spinner(f"Downloading video at {resolution}..."):
        try:
            yt = YouTube(url)
            sanitized_title = sanitize_filename(yt.title)
            stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
            if stream:
                video_file = io.BytesIO()
                stream.stream_to_buffer(video_file)
                video_file.seek(0)
                st.success(f"Processing complete, highest quality available: {resolution}")
                return video_file, f"{sanitized_title}.mp4"
            else:
                raise pytube_exceptions.PytubeError("Stream not found at requested resolution")
        except pytube_exceptions.PytubeError as e:
            st.error(f"Download failed: {str(e)}")
            return None, None


def main():
    st.title("YouTube Video Downloader")
    with st.container(border=True):  # Use a container to hold the input and buttons
        video_url = st.text_input("Enter YouTube Video URL:", key="videoURL")
        submit_url = st.button("Submit URL", key="submit", use_container_width=True)  # Ensure full-width button

    if submit_url:  # Check if the submit button was pressed
        if not video_url:  # Check if the URL field is empty
            st.error("Please enter a YouTube video URL.")
        else:
            resolution = get_highest_resolution(video_url)
            if resolution:
                video_bytes, filename = download_video(video_url, resolution)
                if video_bytes:
                    with st.container(border=False):  # Ensure the download button is full-width
                        st.download_button(label="Download Video", data=video_bytes, file_name=filename,
                                           mime='video/mp4', use_container_width=True)
                else:
                    st.error("Failed to download video.")
            else:
                st.error("Unable to find any video streams.")


if __name__ == "__main__":
    main()
