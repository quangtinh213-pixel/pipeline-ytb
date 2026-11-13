// Chuyển động lặp trong cảnh: compose chép nguyên tệp này vào đầu script của từng mẫu, thay dòng đánh dấu DONG.
// Hữu hạn (không repeat:-1) để timeline tạm dừng render ra đúng từng khung. kieu: bob | xoay | dap | chop | tilt | tho.
function dongLap(tl, sel, kieu, t0, t1, lech) {
  const T = { bob: 2.4, xoay: 6, dap: 1.2, chop: 1.6, tilt: 2.4, tho: 1.4 }[kieu];
  if (!T) return;
  const s = t0 + (lech || 0), n = Math.max(1, Math.floor((t1 - s) / T));
  const nua = { duration: T / 2, ease: "sine.inOut", yoyo: true, repeat: 2 * n - 1 };
  if (kieu === "bob") tl.to(sel, Object.assign({ y: -14 }, nua), s);
  else if (kieu === "dap") tl.to(sel, Object.assign({ scale: 1.04 }, nua), s);
  else if (kieu === "tilt") tl.to(sel, Object.assign({ y: -10, rotationZ: 2.5 }, nua), s);
  else if (kieu === "tho") tl.to(sel, Object.assign({ scaleY: 1.05, scaleX: 0.96, transformOrigin: "50% 100%" }, nua), s);
  else if (kieu === "chop") tl.to(sel, Object.assign({ filter: "brightness(1.25)" }, nua), s);
  else tl.to(sel, { rotationY: 360 * n, transformPerspective: 900, duration: T * n, ease: "none" }, s);
}

// Camera áp lên "thế giới" của cảnh. kieu: day-vao | keo-ra | lia | he-lo | punch-in | lac; "" hoặc "dung" là đứng yên.
// Hữu hạn và đi theo timeline (render tạm dừng ra đúng từng khung); dur là thời lượng chuyển động tính từ t0.
function mayQuay(tl, sel, kieu, t0, dur) {
  const o = { transformOrigin: "50% 55%" };
  if (kieu === "day-vao") tl.fromTo(sel, Object.assign({ scale: 1 }, o), Object.assign({ scale: 1.2, duration: dur, ease: "sine.inOut" }, o), t0);
  else if (kieu === "keo-ra") tl.fromTo(sel, Object.assign({ scale: 1.22 }, o), Object.assign({ scale: 1, duration: dur, ease: "sine.inOut" }, o), t0);
  else if (kieu === "lia") tl.fromTo(sel, { x: 70 }, { x: -70, duration: dur, ease: "sine.inOut" }, t0);
  else if (kieu === "he-lo") tl.fromTo(sel, Object.assign({ scale: 1.35 }, o), Object.assign({ scale: 1, duration: dur * 0.4, ease: "power3.out" }, o), t0);
  else if (kieu === "punch-in") tl.fromTo(sel, Object.assign({ scale: 1 }, o), Object.assign({ scale: 1.22, duration: 0.35, ease: "back.out(1.8)" }, o), t0);
  else if (kieu === "lac") {
    tl.to(sel, { x: -8, y: 4, duration: 0.05, ease: "none" }, t0);
    tl.to(sel, { x: 8, y: -4, duration: 0.05, ease: "none" }, t0 + 0.05);
    tl.to(sel, { x: -4, y: 2, duration: 0.05, ease: "none" }, t0 + 0.1);
    tl.to(sel, { x: 0, y: 0, duration: 0.08, ease: "power2.out" }, t0 + 0.15);
  }
}
