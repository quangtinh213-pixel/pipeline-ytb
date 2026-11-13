from tttc.dang import client
import json

yt = client()

# Update Video 5
v5_id = "RX21zw1F8S0"
new_title_v5 = "SỐC: Ông chủ Nvidia bất ngờ từ chức! Lời hứa biến Việt Nam thành cứ điểm AI có tan thành mây khói?"
v5_resp = yt.videos().list(part="snippet", id=v5_id).execute()
if v5_resp["items"]:
    snippet = v5_resp["items"][0]["snippet"]
    old_title = snippet["title"]
    snippet["title"] = new_title_v5
    update_resp = yt.videos().update(part="snippet", body={"id": v5_id, "snippet": snippet}).execute()
    print(f"Updated V5 ({v5_id}):\n  Cũ: {old_title}\n  Mới: {update_resp['snippet']['title']}")

# Update Video 2
v2_id = "w60qG6ipY1s"
new_title_v2 = "Cấm bán iPhone cũ: Dân buôn ôm nợ, người dùng sắp phải mua máy đắt gấp đôi?"
v2_resp = yt.videos().list(part="snippet", id=v2_id).execute()
if v2_resp["items"]:
    snippet = v2_resp["items"][0]["snippet"]
    old_title = snippet["title"]
    snippet["title"] = new_title_v2
    update_resp = yt.videos().update(part="snippet", body={"id": v2_id, "snippet": snippet}).execute()
    print(f"Updated V2 ({v2_id}):\n  Cũ: {old_title}\n  Mới: {update_resp['snippet']['title']}")
