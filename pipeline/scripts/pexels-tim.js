// Dán vào javascript_tool khi trình duyệt có sẵn đang mở một trang bất kỳ của pexels.com.
// Rồi gọi: await pxl("container port aerial", 4)  → danh sách clip ngang 8–40 s có bản 1920×1080.
// Đọc dữ liệu trang tìm kiếm công khai (__NEXT_DATA__), không cần khoá API. Bỏ qua video AI tài trợ.
window.pxl = async (q, n = 4) => {
  const find = (o, k, out = []) => { if (o && typeof o === 'object') { for (const [kk, v] of Object.entries(o)) { if (kk === k) out.push(v); find(v, k, out); } } return out; };
  const h = await (await fetch('/search/videos/' + encodeURIComponent(q) + '/?orientation=landscape')).text();
  const j = JSON.parse(h.match(/<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/)[1]);
  const data = find(j, 'data').find(d => Array.isArray(d) && d.length && d[0].attributes) || [];
  const out = [];
  for (const d of data) {
    const a = d.attributes || {};
    if (a.type && a.type !== 'video') continue;
    const vid = a.video || {};
    const f = (vid.video_files || a.video_files || []).find(x => x.width === 1920 && x.height === 1080);
    const dur = vid.duration || a.duration;
    if (!f || !dur || dur < 8 || dur > 40) continue;
    out.push({id: a.id || d.id, title: a.title, dur, link: f.link,
              user: a.user ? ((a.user.first_name || '') + ' ' + (a.user.last_name || '')).trim() : '',
              page: 'https://www.pexels.com/video/' + (a.id || d.id) + '/'});
    if (out.length >= n) break;
  }
  return out;
};
