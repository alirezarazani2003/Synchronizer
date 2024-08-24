import csv
import re
import webvtt

def read_vtt_file(file_path):
    return webvtt.read(file_path)

def write_csv_file(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['time', 'synced_primary_subtitle', 'synced_secondary_subtitle'])
        for row in data:
            csvwriter.writerow(row)

def remove_tags(text):
    # Remove HTML tags using regular expressions
    clean_text = re.sub(r'<.*?>', '', text)
    return clean_text

def create_csv_data(primary_vtt, secondary_vtt):
    data = []
    for primary_caption, secondary_caption in zip(primary_vtt, secondary_vtt):
        time = f"{primary_caption.start} --> {primary_caption.end}"
        primary_text = ' '.join(primary_caption.lines)
        secondary_text = ' '.join(secondary_caption.lines)
        # Remove tags from the text
        primary_text = remove_tags(primary_text)
        secondary_text = remove_tags(secondary_text)
        data.append([time, primary_text, secondary_text])
    return data

def main():
    # File paths
    synced_primary_subtitle_path = 'output/synced_primary_subtitle.vtt'
    synced_secondary_subtitle_path = 'output/synced_secondary_subtitle.vtt'
    output_csv_path ='output/subtitle.csv'
    
    # Read .vtt files
    primary_vtt = read_vtt_file(synced_primary_subtitle_path)
    secondary_vtt = read_vtt_file(synced_secondary_subtitle_path)
    
    # Create CSV data
    csv_data = create_csv_data(primary_vtt, secondary_vtt)
    
    # Write to CSV file
    write_csv_file(output_csv_path, csv_data)

if __name__ == '__main__':
    main()
