(()=>{
  "use strict";
  const root=document.querySelector("[data-inventory]");
  const form=root?.querySelector("[data-listing-filters]");
  const actions=root?.querySelector(".marketplace-actions");
  const saved=window.SmartCitySavedSearches;
  const account=window.SmartCityMarketplaceAccount;
  if(!root||!form||!actions||!saved||!account||actions.querySelector("[data-save-search]"))return;

  const type=root.dataset.listingType==="rent"?"rent":"sale";
  const button=document.createElement("button");
  button.type="button";
  button.className="btn marketplace-save-search";
  button.dataset.saveSearch="";
  button.innerHTML='<span aria-hidden="true">☆</span><span>Lưu tìm kiếm</span>';
  const message=document.createElement("span");
  message.className="marketplace-save-search-status";
  message.setAttribute("role","status");
  actions.append(button,message);

  const criteria=()=>({listing_type:type,...Object.fromEntries(new FormData(form))});
  const setMessage=(text,kind="")=>{message.textContent=text||"";message.className=`marketplace-save-search-status${kind?` is-${kind}`:""}`;};
  const setSaved=label=>{
    button.classList.add("is-saved");
    button.innerHTML='<span aria-hidden="true">✓</span><span>Đã lưu tìm kiếm</span>';
    setMessage(label?`Đã lưu: ${label}`:"Đã lưu bộ lọc này.","success");
  };
  const resetState=()=>{
    button.classList.remove("is-saved");
    button.innerHTML='<span aria-hidden="true">☆</span><span>Lưu tìm kiếm</span>';
    setMessage("");
  };

  form.addEventListener("input",resetState);
  form.addEventListener("change",resetState);
  form.addEventListener("reset",()=>setTimeout(resetState,0));

  button.addEventListener("click",async()=>{
    if(button.disabled)return;
    button.disabled=true;setMessage("Đang lưu…");
    const search=criteria();
    try{
      const session=await account.validSession();
      if(!session){
        saved.savePending(search);
        location.href="/tai-khoan-smart-city/?save_search=1";
        return;
      }
      const row=await saved.save(search);
      setSaved(row?.label||"");
    }catch(error){
      if(error?.status===401){
        saved.savePending(search);
        location.href="/tai-khoan-smart-city/?save_search=1";
        return;
      }
      setMessage(error?.message||"Chưa lưu được tìm kiếm. Vui lòng thử lại.","error");
    }finally{button.disabled=false;}
  });
})();
