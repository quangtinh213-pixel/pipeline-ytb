from tttc.dang import client

yt = client()

# 1. Short 1: s0OF-ADnF80 -> Long video: w60qG6ipY1s
s1_id = "s0OF-ADnF80"
s1_resp = yt.videos().list(part="snippet", id=s1_id).execute()
if s1_resp["items"]:
    snip1 = s1_resp["items"][0]["snippet"]
    link_line1 = "👉 Xem video phân tích chi tiết đầy đủ tại: https://youtu.be/w60qG6ipY1s\n\n"
    if "w60qG6ipY1s" not in snip1["description"]:
        snip1["description"] = link_line1 + snip1["description"]
        yt.videos().update(part="snippet", body={"id": s1_id, "snippet": snip1}).execute()
        print(f"Updated Short 1 ({s1_id}) with link to w60qG6ipY1s")

# 2. Short 2: XwsTqRMwMWA -> Long video: GXoScbOFOQE
s2_id = "XwsTqRMwMWA"
s2_resp = yt.videos().list(part="snippet", id=s2_id).execute()
if s2_resp["items"]:
    snip2 = s2_resp["items"][0]["snippet"]
    link_line2 = "👉 Xem video bóc tách chi tiết đầy đủ tại: https://youtu.be/GXoScbOFOQE\n\n"
    if "GXoScbOFOQE" not in snip2["description"]:
        snip2["description"] = link_line2 + snip2["description"]
        yt.videos().update(part="snippet", body={"id": s2_id, "snippet": snip2}).execute()
        print(f"Updated Short 2 ({s2_id}) with link to GXoScbOFOQE")
