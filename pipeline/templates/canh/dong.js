// Chuyển động lặp trong cảnh: compose chép nguyên tệp này vào đầu script của từng mẫu, thay dòng đánh dấu DONG.
// Hữu hạn (không repeat:-1) để timeline tạm dừng render ra đúng từng khung. kieu: bob | xoay | dap | chop.
function dongLap(tl, sel, kieu, t0, t1, lech) {
  const T = { bob: 2.4, xoay: 6, dap: 1.2, chop: 1.6 }[kieu];
  if (!T) return;
  const s = t0 + (lech || 0), n = Math.max(1, Math.floor((t1 - s) / T));
  const nua = { duration: T / 2, ease: "sine.inOut", yoyo: true, repeat: 2 * n - 1 };
  if (kieu === "bob") tl.to(sel, Object.assign({ y: -14 }, nua), s);
  else if (kieu === "dap") tl.to(sel, Object.assign({ scale: 1.04 }, nua), s);
  else if (kieu === "chop") tl.to(sel, Object.assign({ filter: "brightness(1.25)" }, nua), s);
  else tl.to(sel, { rotationY: 360 * n, transformPerspective: 900, duration: T * n, ease: "none" }, s);
}
