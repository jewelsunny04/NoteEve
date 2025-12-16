import requests

base_url = "https://www.eci.gov.in/sir/f3/S24/data/OLDSIRROLL/S24/322/"
output_folder = "downloads/"  # ensure this folder exists or create it

for i in range(1, 279):  # 1 to 278 inclusive
    file_name = f"S24_322_{i}.pdf"
    url = base_url + file_name
    output_path = output_folder + file_name
    try:
        print(f"Downloading {url} …")
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Saved to {output_path}")
        else:
            print(f"Failed to download {url} — status code {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")