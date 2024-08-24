import requests
import json

def write_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)

def read_vtt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_vtt_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def create_json_request(primary_subtitle, secondary_subtitle, primary_language, secondary_language):
    return {
        "primary_subtitle": primary_subtitle,
        "secondary_subtitle": secondary_subtitle,
        "primary_language": primary_language,
        "secondary_language": secondary_language
    }

def send_request(json_data, url):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(json_data))
    return response.json()


def main():
    # File paths
    primary_subtitle_path = 'en_70105212.vtt'
    secondary_subtitle_path = 'de_70105212.vtt'
    
    # Read .vtt files
    primary_subtitle = read_vtt_file(primary_subtitle_path)
    secondary_subtitle = read_vtt_file(secondary_subtitle_path)
    
    # Create JSON request
    json_data = create_json_request(primary_subtitle, secondary_subtitle, 'en', 'fr')
    write_json_file("output/sync request.json",json_data)    # URL of the FastAPI service
    url = 'http://localhost:8000/get_sync_subs'
    
    # Send request and get response
    response = send_request(json_data, url)
    write_json_file("output/sync response.json",response)
    # Write synchronized subtitles to new .vtt files
    write_vtt_file('output/synced_primary_subtitle.vtt', response['primary_subtitle'])
    write_vtt_file('output/synced_secondary_subtitle.vtt', response['secondary_subtitle'])



if __name__ == '__main__':
    main()
