/*!
 * app-shell.js — điều hướng dùng chung cho timmuasmartcity.com
 * Cập nhật 12/08/2026: đưa Cẩm nang mua nhà ra desktop + homepage.
 */
(function () {
  "use strict";

  var SDT = "0977923284";

  function laDienThoai() {
    return window.matchMedia("(max-width:640px)").matches;
  }

  function duongDan() {
    var p = location.pathname.replace(/index\.html$/, "");
    if (p.length > 1 && p.charAt(p.length - 1) !== "/") return p;
    return p;
  }

  function tabDangMo() {
    var p = duongDan();
    if (p === "/" || p === "") return "trang-chu";
    if (p.indexOf("/blog/") === 0) return "cam-nang";
    return "";
  }

  var IC = {
    nha: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M3.5 10.5 12 4l8.5 6.5V19a1 1 0 0 1-1 1h-5v-6h-5v6h-5a1 1 0 0 1-1-1Z"/></svg>',
    sach: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10a2 2 0 0 1 2 2v13a2 2 0 0 0-2-2H5.5A1.5 1.5 0 0 1 4 15.5Z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14a2 2 0 0 0-2 2v13a2 2 0 0 1 2-2h4.5a1.5 1.5 0 0 0 1.5-1.5Z"/></svg>',
    kygui: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M3.5 10.5 12 4l8.5 6.5V19a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1Z"/><path d="M12 16v-5M9.6 13.2 12 10.8l2.4 2.4" stroke-linecap="round"/></svg>',
    chiakhoa: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><circle cx="8" cy="12" r="3.4"/><path d="M11.4 12H20M17 12v3M20 12v2.4" stroke-linecap="round"/></svg>',
    menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="5" cy="12" r="1.4" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1.4" fill="currentColor" stroke="none"/></svg>'
  };

  var MENU = [
    { nhom: "Cẩm nang mua nhà" },
    { ten: "Tất cả bài hướng dẫn", href: "/blog/" },
    { ten: "Giá bán Vinhomes Smart City", href: "/blog/gia-ban-vinhomes-smart-city/" },
    { ten: "Kinh nghiệm mua căn hộ", href: "/blog/kinh-nghiem-mua-can-ho-vinhomes-smart-city/" },
    { ten: "So sánh các phân khu", href: "/blog/so-sanh-phan-khu-vinhomes-smart-city/" },
    { nhom: "Liên hệ" },
    { ten: "Nhắn Zalo " + SDT, href: "https://zalo.me/" + SDT, ngoai: true, zalo: true },
    { ten: "Gọi " + SDT, href: "tel:" + SDT },
    { nhom: "Xem căn" },
    { ten: "Toàn bộ căn đang bán", href: "/#filtersSection" },
    { ten: "Ký gửi bán căn", href: "https://zalo.me/" + SDT, ngoai: true },
    { nhom: "Bên cho thuê" },
    { ten: "Cẩm nang thuê nhà", href: "https://timthuesmartcity.com/cam-nang-thue-nha.html", ngoai: true },
    { ten: "Xem căn cho thuê Smart City", href: "https://timthuesmartcity.com", ngoai: true }
  ];

  function dungMenuHtml() {
    var h = '<div class="tbs-head"><strong>Menu</strong>'
          + '<button type="button" id="tbsDong" aria-label="Đóng">&times;</button></div>';
    for (var i = 0; i < MENU.length; i++) {
      var m = MENU[i];
      if (m.nhom) { h += '<div class="tbs-nhom">' + m.nhom + '</div>'; continue; }
      h += '<a href="' + m.href + '"'
         + (m.ngoai ? ' target="_blank" rel="noopener"' : '')
         + (m.zalo ? ' class="tbs-zalo"' : '')
         + '>' + m.ten + '</a>';
    }
    return h;
  }

  function boSungCamNangDesktop() {
    var nav = document.querySelector(".topnav");
    if (!nav || nav.querySelector('a[href="/blog/"]')) return;
    var link = document.createElement("a");
    link.href = "/blog/";
    link.textContent = "Cẩm nang";
    var timThue = nav.querySelector('a[href^="https://timthuesmartcity.com"]');
    if (timThue) nav.insertBefore(link, timThue);
    else nav.appendChild(link);
  }

  function chenKhoiCamNangTrangChu() {
    var p = duongDan();
    if (!(p === "/" || p === "") || document.getElementById("cam-nang-mua-nha")) return;

    if (!document.getElementById("style-cam-nang-home")) {
      var style = document.createElement("style");
      style.id = "style-cam-nang-home";
      style.textContent =
        '.cam-nang-home{max-width:1180px;margin:44px auto 72px;padding:0 20px}.cam-nang-home__head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:18px}.cam-nang-home h2{margin:0;font-size:clamp(26px,3vw,38px);line-height:1.2}.cam-nang-home__head p{margin:7px 0 0;color:#65707c}.cam-nang-home__all{font-weight:700;color:#b71925;text-decoration:none;white-space:nowrap}.cam-nang-home__grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.cam-nang-home__card{display:block;background:#fff;border:1px solid #e8eaed;border-radius:18px;padding:20px;text-decoration:none;color:inherit;box-shadow:0 8px 24px rgba(15,23,42,.05)}.cam-nang-home__card strong{display:block;font-size:18px;line-height:1.4;margin-bottom:7px}.cam-nang-home__card span{display:block;color:#667085;line-height:1.55}.cam-nang-home__card:hover{transform:translateY(-2px);box-shadow:0 12px 28px rgba(15,23,42,.08)}@media(max-width:800px){.cam-nang-home__grid{grid-template-columns:1fr}.cam-nang-home__head{align-items:start;flex-direction:column}.cam-nang-home{margin-top:32px}}';
      document.head.appendChild(style);
    }

    var sec = document.createElement("section");
    sec.id = "cam-nang-mua-nha";
    sec.className = "cam-nang-home";
    sec.setAttribute("aria-labelledby", "cam-nang-home-title");
    sec.innerHTML =
      '<div class="cam-nang-home__head"><div><h2 id="cam-nang-home-title">Cẩm nang mua căn hộ Smart City</h2><p>Giá bán, kinh nghiệm mua chuyển nhượng và cách chọn căn theo nhu cầu thực tế.</p></div><a class="cam-nang-home__all" href="/blog/">Xem tất cả bài viết →</a></div>' +
      '<div class="cam-nang-home__grid">' +
        '<a class="cam-nang-home__card" href="/blog/gia-ban-vinhomes-smart-city/"><strong>Giá bán Vinhomes Smart City 2026</strong><span>Cách đọc tổng giá và giá/m² để so căn cùng nhóm.</span></a>' +
        '<a class="cam-nang-home__card" href="/blog/kinh-nghiem-mua-can-ho-vinhomes-smart-city/"><strong>Kinh nghiệm mua căn hộ</strong><span>Checklist xem căn, kiểm tra giấy tờ và đặt cọc.</span></a>' +
        '<a class="cam-nang-home__card" href="/blog/so-sanh-phan-khu-vinhomes-smart-city/"><strong>So sánh các phân khu</strong><span>Chọn khu theo ngân sách, vị trí và nhu cầu ở thực.</span></a>' +
        '<a class="cam-nang-home__card" href="/blog/mua-can-ho-2pn-vinhomes-smart-city/"><strong>Mua căn 2PN Smart City</strong><span>Cách chọn 2PN theo layout, số WC, tầng và hướng.</span></a>' +
        '<a class="cam-nang-home__card" href="/blog/sapphire-vinhomes-smart-city/"><strong>Sapphire Vinhomes Smart City</strong><span>Kinh nghiệm so căn chuyển nhượng trong nhóm Sapphire.</span></a>' +
        '<a class="cam-nang-home__card" href="/blog/the-sakura-vinhomes-smart-city/"><strong>The Sakura Smart City</strong><span>Những yếu tố cần kiểm tra trước khi mua căn Sakura.</span></a>' +
      '</div>';

    var footer = document.querySelector("footer");
    if (footer && footer.parentNode) footer.parentNode.insertBefore(sec, footer);
    else document.body.appendChild(sec);
  }

  function dung() {
    if (document.querySelector(".tabbar")) return;

    var mo = tabDangMo();
    function lop(k) { return mo === k ? ' class="dang-o-day"' : ''; }

    var bar = document.createElement("nav");
    bar.className = "tabbar";
    bar.setAttribute("aria-label", "Điều hướng nhanh");
    bar.innerHTML =
        '<a href="/"' + lop("trang-chu") + '>' + IC.nha + '<span>Trang chủ</span></a>'
      + '<a href="/blog/"' + lop("cam-nang") + '>' + IC.sach + '<span>Cẩm nang</span></a>'
      + '<a href="https://zalo.me/' + SDT + '" target="_blank" rel="noopener">'
        + IC.kygui + '<span>Ký gửi bán</span></a>'
      + '<button type="button" id="tabMenu" aria-haspopup="dialog">' + IC.menu + '<span>Menu</span></button>';

    var nen = document.createElement("div");
    nen.className = "tabbar-backdrop";

    var sheet = document.createElement("div");
    sheet.className = "tabbar-sheet";
    sheet.setAttribute("role", "dialog");
    sheet.setAttribute("aria-label", "Menu");
    sheet.innerHTML = dungMenuHtml();

    document.body.appendChild(nen);
    document.body.appendChild(sheet);
    document.body.appendChild(bar);

    function moMenu() { sheet.classList.add("open"); nen.classList.add("open"); }
    function dongMenu() { sheet.classList.remove("open"); nen.classList.remove("open"); }

    document.getElementById("tabMenu").addEventListener("click", moMenu);
    document.getElementById("tbsDong").addEventListener("click", dongMenu);
    nen.addEventListener("click", dongMenu);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") dongMenu();
    });
    sheet.addEventListener("click", function (e) {
      if (e.target.closest("a")) dongMenu();
    });
  }

  function khoiDong() {
    try {
      boSungCamNangDesktop();
      chenKhoiCamNangTrangChu();
      if (laDienThoai()) dung();
    } catch (e) { /* điều hướng phụ hỏng không được kéo sập trang */ }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", khoiDong);
  } else {
    khoiDong();
  }
  window.addEventListener("resize", khoiDong);
})();
