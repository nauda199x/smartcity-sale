(()=>{
  "use strict";
  const dashboard=document.querySelector("[data-member-dashboard]");
  const list=document.querySelector("[data-saved-search-list]");
  const totalNode=document.querySelector("[data-count-new-matches]");
  const status=document.querySelector("[data-saved-search-status]");
  const saved=window.SmartCitySavedSearches;
  const account=window.SmartCityMarketplaceAccount;
  if(!dashboard||!list||!saved||!account)return;

  let running=null;
  let appliedPending=false;

  const setStatus=(text,kind="")=>{
    if(!status)return;
    status.hidden=!text;
    status.textContent=text||"";
    status.className=`member-status member-saved-search-status${kind?` is-${kind}`:""}`;
  };
  const formatPrice=(value,type)=>{
    const amount=Number(value||0);if(!amount)return "";
    if(type==="rent")return `${new Intl.NumberFormat("vi-VN",{maximumFractionDigits:1}).format(amount/1e6)} triệu/tháng`;
    return `${new Intl.NumberFormat("vi-VN",{maximumFractionDigits:1}).format(amount/1e9)} tỷ`;
  };
  const descriptionFor=row=>{
    const parts=[];
    if(row.keyword)parts.push(`Từ khóa: ${row.keyword}`);
    if(row.phase)parts.push(row.phase);
    if(row.tower)parts.push(row.tower);
    if(row.unit_type)parts.push(row.unit_type);
    if(row.min_price_vnd&&row.max_price_vnd)parts.push(`${formatPrice(row.min_price_vnd,row.listing_type)} – ${formatPrice(row.max_price_vnd,row.listing_type)}`);
    else if(row.min_price_vnd)parts.push(`Từ ${formatPrice(row.min_price_vnd,row.listing_type)}`);
    else if(row.max_price_vnd)parts.push(`Đến ${formatPrice(row.max_price_vnd,row.listing_type)}`);
    if(row.min_area_sqm!==null&&row.min_area_sqm!==undefined&&row.max_area_sqm!==null&&row.max_area_sqm!==undefined)parts.push(`${row.min_area_sqm}–${row.max_area_sqm} m²`);
    else if(Number(row.min_area_sqm)>0)parts.push(`Từ ${row.min_area_sqm} m²`);
    if(row.furnishing)parts.push(row.furnishing);
    return parts.join(" · ")||"Tất cả căn phù hợp với loại giao dịch đã lưu.";
  };

  const empty=()=>{
    list.replaceChildren();
    const box=document.createElement("div");box.className="member-saved-search-empty";
    const strong=document.createElement("strong");strong.textContent="Chưa có tìm kiếm nào được lưu.";
    const p=document.createElement("p");p.textContent="Mở sàn mua bán hoặc cho thuê, chọn bộ lọc rồi bấm “Lưu tìm kiếm”.";
    box.append(strong,p);list.append(box);
    if(totalNode)totalNode.textContent="0";
  };

  const cardFor=(row,newCount,countError=false)=>{
    const card=document.createElement("article");card.className="member-saved-search-card";
    const body=document.createElement("div");
    const title=document.createElement("h3");title.textContent=row.label||saved.labelFor(row);
    const desc=document.createElement("p");desc.textContent=descriptionFor(row);
    const meta=document.createElement("div");meta.className="member-saved-search-meta";
    const badge=document.createElement("span");badge.className=`member-saved-search-badge${countError?" is-error":newCount>0?" has-new":""}`;
    badge.textContent=countError?"Chưa đếm được căn mới":newCount>0?`${newCount} căn mới`:"Chưa có căn mới";
    const since=document.createElement("span");since.className="member-saved-search-badge";
    const date=new Date(row.last_seen_at||row.created_at||"");
    since.textContent=Number.isNaN(date.getTime())?"Đã lưu":"Từ lần xem "+date.toLocaleDateString("vi-VN");
    meta.append(badge,since);body.append(title,desc,meta);

    const actions=document.createElement("div");actions.className="member-saved-search-actions";
    const open=document.createElement("a");open.href=saved.urlFor(row);open.textContent=newCount>0?`Xem ${newCount} căn mới`:"Xem kết quả";
    open.addEventListener("click",async event=>{
      if(event.button||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
      event.preventDefault();open.textContent="Đang mở…";
      try{await saved.touch(row.id);}catch{}
      location.href=saved.urlFor(row);
    });
    const remove=document.createElement("button");remove.type="button";remove.className="is-delete";remove.textContent="Xóa";
    remove.addEventListener("click",async()=>{
      if(!confirm("Xóa tìm kiếm đã lưu này?"))return;
      remove.disabled=true;remove.textContent="Đang xóa…";
      try{await saved.remove(row.id);await render(true);}catch(error){remove.disabled=false;remove.textContent="Xóa";setStatus(error?.message||"Chưa xóa được tìm kiếm.","error");}
    });
    actions.append(open,remove);card.append(body,actions);return card;
  };

  const applyPending=async()=>{
    if(appliedPending)return false;
    const pending=saved.readPending();
    if(!pending)return false;
    appliedPending=true;
    try{
      const row=await saved.save(pending);
      saved.clearPending();
      setStatus(`Đã lưu tìm kiếm “${row?.label||saved.labelFor(saved.normalize(pending))}”. Từ giờ mục này sẽ báo số căn mới kể từ lần bạn xem.`,"success");
      return true;
    }catch(error){
      appliedPending=false;
      setStatus(error?.message||"Chưa lưu được bộ lọc. Vui lòng thử lại.","error");
      return false;
    }
  };

  async function render(force=false){
    if(dashboard.hidden)return;
    if(running&&!force)return running;
    running=(async()=>{
      const session=await account.validSession();
      if(!session)return;
      await applyPending();
      list.replaceChildren();
      const loading=document.createElement("div");loading.className="member-saved-search-empty";loading.textContent="Đang kiểm tra căn mới…";list.append(loading);
      let rows=[];
      try{rows=await saved.list();}catch(error){list.replaceChildren();setStatus(error?.message||"Chưa tải được tìm kiếm đã lưu.","error");if(totalNode)totalNode.textContent="0";return;}
      if(!rows.length){empty();return;}
      const results=await Promise.all(rows.map(async row=>{
        try{return {row,count:await saved.countMatches(row,{newOnly:true}),error:false};}
        catch{return {row,count:0,error:true};}
      }));
      const total=results.reduce((sum,item)=>sum+item.count,0);
      if(totalNode)totalNode.textContent=String(total);
      list.replaceChildren(...results.map(item=>cardFor(item.row,item.count,item.error)));
    })();
    try{return await running;}finally{running=null;}
  }

  const observer=new MutationObserver(()=>{if(!dashboard.hidden)render().catch(()=>{});});
  observer.observe(dashboard,{attributes:true,attributeFilter:["hidden"]});
  if(!dashboard.hidden)render().catch(()=>{});
})();
