from fastapi import FastAPI
import datetime
import webvtt
from webvtt import Caption, WebVTT

app = FastAPI()


@app.post("/get_sync_subs")
def get_sync(json: dict):
    data = json

    sub_one_req = data["primary_subtitle"]
    sub_two_req = data["secondary_subtitle"]
    sub_one_name = data["primary_language"]
    sub_two_name = data["secondary_language"]
    sub_one = json_to_vtt(sub_one_req, sub_one_name)
    sub_two = json_to_vtt(sub_two_req, sub_two_name)
    synced_subs = get_sync_subs(sub_one, sub_two)
    data["primary_subtitle"] = conver_vtt_to_str(synced_subs[0])
    data["secondary_subtitle"] = conver_vtt_to_str(synced_subs[1])
    # data["status"] = "synchronized"
    return data


def json_to_vtt(json_value1, name1):
    file1 = json_value1.split("\n")
    file1_to_breaked_str = ""
    for i in file1:
        file1_to_breaked_str += i + "\n"
    file = open(f"files/{name1}.vtt", "w", encoding="utf-8")
    file.write(file1_to_breaked_str)
    file.close()
    file = webvtt.read(f"files/{name1}.vtt")
    return file

def inside(time_a, time_b):
    return time_a[0] <= (time_b[0] + time_b[1]) / 2 <= time_a[1]

def sync(texts_a, texts_b, times_a, times_b):
    a = 0
    while a < len(texts_a):
        b = 0
        while b < len(texts_b):
            if times_b[b][0] > times_a[a][1]:
                break
            if inside(times_a[a], times_b[b]):
                if abs(times_a[a][0] - times_a[a][1]) > abs(
                    times_b[b][0] - times_b[b][1]
                ):
                    times_b[b] = times_a[a]
                else:
                    times_a[a] = times_b[b]
            b += 1
        a += 1

def make_time_float(x):
    parts = x.split(":")
    data = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return data

def parse(sub_vtt, texts, times):
    vtt = sub_vtt

    for caption in vtt:
        times.append([make_time_float(caption.start), make_time_float(caption.end)])
        texts.append(caption.raw_text)

def make_subtitle(texts, times):
    vtt = WebVTT()
    for i in range(len(times)):
        caption = Caption(
                str(datetime.timedelta(seconds=times[i][0])) + ".000",
            str(datetime.timedelta(seconds=times[i][1])) + ".000",
            texts[i],
        )
        vtt.captions.append(caption)
    return vtt

def get_sync_subs(first_sub, second_sub):
    texts_a = []
    texts_b = []
    times_a = []
    times_b = []
    parse(first_sub, texts_a, times_a)
    parse(second_sub, texts_b, times_b)
    sync(texts_a, texts_b, times_a, times_b)
    sync(texts_b, texts_a, times_b, times_a)
    result_1 = make_subtitle(texts_a, times_a)
    result_2 = make_subtitle(texts_b, times_b)
    return [result_1, result_2]


def conver_vtt_to_str(vtt_sub) -> str:
    output = ["WEBVTT"]
    response = ""
    counter = 1
    for caption in range(len(vtt_sub)):
        try:
            if vtt_sub[caption].text != vtt_sub[caption + 1].text:
                caption = vtt_sub[caption]
                output.append("")
                output.append(
                    "{}\n{} --> {}".format(counter, caption.start, caption.end)
                )
                output.extend(caption.lines)  
                counter += 1
        except Exception as e:
            pass

    response = "\n".join(output)
    return response
