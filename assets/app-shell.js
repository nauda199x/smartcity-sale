/* Shared public-shell enhancer.
   Important: this file must NEVER replace the canonical header/footer rendered in HTML.
   Older versions did that and injected legacy routes from a previous site architecture. */
(function(){
  "use strict";

  function markCurrentNavigation(){
    const path=location.pathname.replace(/index\.html$/,"");
    document.querySelectorAll(".site-header a[href], .nav-links a[href]").forEach(link=>{
      let href="";
      try{href=new URL(link.getAttribute("href"),location.origin).pathname.replace(/index\.html$/,"");}catch{return;}
      const exact=href===path;
      const section=href!=="/" && path.startsWith(href);
      if(exact || section) link.setAttribute("aria-current","page");
      else link.removeAttribute("aria-current");
    });
  }

  function addDirectListingCta(){
    const nav=document.querySelector(".nav-links");
    if(!nav || nav.querySelector(".nav-direct-cta")) return;
    const cta=document.createElement("a");
    cta.className="nav-direct-cta";
    cta.href="/dang-tin-smart-city/";
    cta.textContent="Đăng tin";
    nav.append(cta);
  }

  function addPosterAccountLink(){
    const nav=document.querySelector(".nav-links");
    if(!nav || nav.querySelector('[href="/tai-khoan-smart-city/"]')) return;
    const link=document.createElement("a");
    link.className="nav-account-link";
    link.href="/tai-khoan-smart-city/";
    link.textContent="Tài khoản";
    const cta=nav.querySelector(".nav-direct-cta");
    if(cta)nav.insertBefore(link,cta);else nav.append(link);
  }

  function loadPosterAccountEnhancer(){
    if(location.pathname.startsWith("/admin"))return;
    if(!document.querySelector("[data-marketplace-submit]") && !location.pathname.startsWith("/tai-khoan-smart-city/"))return;
    if(!document.querySelector('link[href*="marketplace-account.css"]')){
      const style=document.createElement("link");
      style.rel="stylesheet";
      style.href="/assets/css/marketplace-account.css?v=20260908-account1";
      document.head.append(style);
    }
    if(window.SmartCityAccount || document.querySelector('script[src*="marketplace-account.js"]'))return;
    // Account code is intentionally loaded after the core marketplace. It patches
    // createListing on the shared API object before a human can submit the form,
    // while keeping anonymous posting working when there is no user session.
    const script=document.createElement("script");
    script.src="/assets/js/marketplace-account.js?v=20260908-account1";
    script.defer=true;
    document.head.append(script);
  }

  function addMobilePropertyNav(){
    if(document.querySelector(".mobile-property-nav")) return;
    if(document.body.classList.contains("listing-detail-page")) return;
    if(document.querySelector("[data-marketplace-submit]")) return;
    if(location.pathname.startsWith("/admin")) return;

    const nav=document.createElement("nav");
    nav.className="mobile-property-nav";
    nav.setAttribute("aria-label","Điều hướng nhanh trên điện thoại");
    const items=[
      ["⌂","Trang chủ","/"],
      ["⌕","Mặt bằng","/mat-bang-smart-city/"],
      ["₫","Mua bán","/mua-ban-smart-city/"],
      ["⌁","Cho thuê","/cho-thue-smart-city/"],
      ["＋","Đăng tin","/dang-tin-smart-city/"]
    ];
    items.forEach(([icon,label,href])=>{
      const a=document.createElement("a");
      a.href=href;
      a.innerHTML='<span aria-hidden="true">'+icon+'</span><small>'+label+'</small>';
      const target=new URL(href,location.origin).pathname;
      if((target==="/" && location.pathname==="/") || (target!=="/" && location.pathname.startsWith(target))){
        a.setAttribute("aria-current","page");
      }
      nav.append(a);
    });
    document.body.append(nav);
  }

  function bindHeaderState(){
    const header=document.querySelector(".site-header");
    if(!header) return;
    const sync=()=>header.classList.toggle("is-scrolled",window.scrollY>12);
    sync();
    window.addEventListener("scroll",sync,{passive:true});
  }

  function normalizeLegacyShellClasses(){
    // If an old cached/generated page still contains V2 shell classes, keep it usable
    // without replacing its semantic structure.
    document.querySelectorAll(".site-header__inner").forEach(el=>el.classList.add("nav"));
    document.querySelectorAll(".site-brand").forEach(el=>el.classList.add("brand"));
    document.querySelectorAll(".site-brand__mark").forEach(el=>el.classList.add("brand-mark"));
  }

  function init(){
    document.documentElement.classList.add("real-estate-ui");
    document.body.classList.add("real-estate-portal");
    normalizeLegacyShellClasses();
    addDirectListingCta();
    addPosterAccountLink();
    markCurrentNavigation();
    addMobilePropertyNav();
    bindHeaderState();
    loadPosterAccountEnhancer();
  }

  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",init,{once:true});
  else init();
}());
(function prefetchMarketplaceNavigation(){
  const connection=navigator.connection;
  if(connection?.saveData||/2g/.test(connection?.effectiveType||""))return;
  const done=new Set();
  const prefetch=event=>{
    const link=event.target.closest?.('a[href]');if(!link)return;
    const url=new URL(link.href,location.origin);
    if(url.origin!==location.origin||url.search||url.hash||!/^\/(mua-ban-smart-city|cho-thue-smart-city|mat-bang-smart-city|gia-smart-city|tai-khoan-smart-city)\//.test(url.pathname)||done.has(url.href)||done.size>=6)return;
    done.add(url.href);const hint=document.createElement('link');hint.rel='prefetch';hint.href=url.href;document.head.append(hint);
  };
  document.addEventListener('pointerover',prefetch,{passive:true});document.addEventListener('focusin',prefetch);
})();