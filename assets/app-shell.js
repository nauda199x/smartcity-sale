/* Shared, accessible site shell for every public route. */
(function () {
  "use strict";
  var links = [
    ["Tổng quan", "/", "home"],
    ["Dự án & phân khu", "/phan-khu.html", "phan-khu"],
    ["Giá & thị trường", "/gia-ban-vinhomes-smart-city.html", "gia"],
    ["Cẩm nang mua", "/cam-nang.html", "cam-nang"],
    ["Quỹ căn", "/can-ho-dang-ban.html", "can-ho"],
    ["Ký gửi", "/ky-gui-ban-can.html", "ky-gui"]
  ];
  function section(path) {
    if (/phan-khu|sapphire|sakura|gateway|lumiere|masteri|miami|tonkin|imperia|sola|victoria|canopy/.test(path)) return "phan-khu";
    if (/gia-ban/.test(path)) return "gia";
    if (/can-ho-dang-ban|ban-(can-ho|studio)/.test(path)) return "can-ho";
    if (/ky-gui/.test(path)) return "ky-gui";
    if (/cam-nang|kinh-nghiem|chi-phi|mua-can|so-sanh/.test(path)) return "cam-nang";
    return path === "/" || path === "/index.html" ? "home" : "";
  }
  function header() {
    var current = section(location.pathname);
    var nav = links.map(function (item) {
      var currentAttr = current === item[2] ? ' aria-current="page"' : "";
      var cls = item[2] === "can-ho" ? ' class="site-nav__cta"' : "";
      return '<a href="' + item[1] + '"' + cls + currentAttr + '>' + item[0] + '</a>';
    }).join("");
    return '<header class="site-header"><div class="container site-header__inner">' +
      '<a class="site-brand" href="/" aria-label="Tìm Mua Smart City — Trang chủ"><span class="site-brand__mark" aria-hidden="true">S</span><span>Tìm Mua Smart City</span></a>' +
      '<nav class="site-nav" id="siteNav" aria-label="Điều hướng chính">' + nav + '</nav>' +
      '<button class="menu-toggle" type="button" aria-label="Mở menu" aria-controls="siteNav" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>' +
      '</div><div class="site-menu-backdrop"></div></header>';
  }
  function footer() {
    return '<footer class="site-footer"><div class="container"><div class="site-footer__grid">' +
      '<div><a class="site-brand" href="/"><span class="site-brand__mark" aria-hidden="true">S</span><span>Tìm Mua Smart City</span></a><p>Cổng thông tin độc lập dành cho người mua Vinhomes Smart City: hiểu dự án, so sánh phân khu, đọc dữ liệu giá và sàng lọc quỹ căn chuyển nhượng thực tế.</p></div>' +
      '<div><h2>Dự án nổi bật</h2><a href="/masteri-west-heights-smart-city.html">Masteri West Heights</a><a href="/lumiere-evergreen-smart-city.html">LUMIÈRE Evergreen</a><a href="/phan-khu-the-sakura.html">The Sakura</a><a href="/the-canopy-residences-smart-city.html">The Canopy Residences</a></div>' +
      '<div><h2>Dữ liệu người mua</h2><a href="/phan-khu.html">Tất cả phân khu</a><a href="/gia-ban-vinhomes-smart-city.html">Giá & thị trường</a><a href="/can-ho-dang-ban.html">Quỹ căn đang bán</a><a href="/so-sanh-phan-khu-vinhomes-smart-city.html">So sánh phân khu</a></div>' +
      '<div><h2>Cẩm nang</h2><a href="/cam-nang.html">Cẩm nang mua căn</a><a href="/kinh-nghiem-mua-can-ho-vinhomes-smart-city.html">Kinh nghiệm mua</a><a href="/chi-phi-mua-can-ho-chuyen-nhuong-vinhomes-smart-city.html">Thuế phí chuyển nhượng</a><a href="/ky-gui-ban-can.html">Ký gửi bán căn</a></div>' +
      '<div><h2>Liên hệ</h2><a href="tel:0977923284">0977 923 284</a><a href="https://zalo.me/0977923284" rel="noopener">Zalo</a><h2>Pháp lý website</h2><a href="/chinh-sach-bao-mat.html">Chính sách bảo mật</a><a href="/dieu-khoan-su-dung.html">Điều khoản sử dụng</a></div>' +
      '</div><div class="site-footer__legal">Tìm Mua Smart City là cổng thông tin độc lập, không phải website chính thức của Vinhomes hoặc các chủ đầu tư/phát triển dự án. Dữ liệu giá và quỹ căn cần được xác nhận lại trước giao dịch.</div></div></footer>';
  }
  function init() {
    var oldHeader = document.querySelector("body > header");
    if (oldHeader) oldHeader.outerHTML = header(); else document.body.insertAdjacentHTML("afterbegin", header());
    var oldFooter = document.querySelector("body > footer");
    if (oldFooter) oldFooter.outerHTML = footer(); else document.body.insertAdjacentHTML("beforeend", footer());
    var toggle = document.querySelector(".menu-toggle"), nav = document.querySelector(".site-nav"), backdrop = document.querySelector(".site-menu-backdrop");
    if (!toggle || !nav || !backdrop) return;
    function setMenu(open) { nav.classList.toggle("is-open", open); backdrop.classList.toggle("is-open", open); toggle.setAttribute("aria-expanded", String(open)); toggle.setAttribute("aria-label", open ? "Đóng menu" : "Mở menu"); document.body.style.overflow = open ? "hidden" : ""; }
    toggle.addEventListener("click", function () { setMenu(toggle.getAttribute("aria-expanded") !== "true"); });
    backdrop.addEventListener("click", function () { setMenu(false); });
    nav.addEventListener("click", function (event) { if (event.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (event) { if (event.key === "Escape") { setMenu(false); toggle.focus(); } });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
}());
