(()=>{
  "use strict";
  const account=window.SmartCityMarketplaceAccount;
  const api=window.SmartCityMarketplace;
  if(!account||!api)return;

  const authCard=document.querySelector("[data-member-auth]");
  const dashboard=document.querySelector("[data-member-dashboard]");
  const list=document.querySelector("[data-member-list]");
  const identity=document.querySelector("[data-member-identity]");
  const status=document.querySelector("[data-member-status]");
  const tabs=[...document.querySelectorAll("[data-member-tab]")];
  const forms=[...document.querySelectorAll("[data-member-form]")];
  const counts={all:document.querySelector("[data-count-all]"),approved:document.querySelector("[data-count-approved]"),pending:document.querySelector("[data-count-pending]"),hidden:document.querySelector("[data-count-hidden]")};
  const statusLabels={pending:"Chờ duyệt",approved:"Đang hiển thị",rejected:"Bị từ chối",expired:"Đã ẩn / hết hạn",sold:"Đã bán",rented:"Đã cho thuê"};

  const setStatus=(message,type="")=>{
    if(!status)return;
    status.hidden=!message;
    status.textContent=message||"";
    status.className=`member-status${type?` is-${type}`:""}`;
  };

  const setMode=mode=>{
    tabs.forEach(tab=>tab.classList.toggle("is-active",tab.dataset.memberTab===mode));
    forms.forEach(form=>form.hidden=form.dataset.memberForm!==mode);
    setStatus("");
  };

  tabs.forEach(tab=>tab.addEventListener("click",()=>setMode(tab.dataset.memberTab)));

  const buttonBusy=(button,busy,label)=>{
    if(!button)return;
    if(!button.dataset.defaultLabel)button.dataset.defaultLabel=button.textContent;
    button.disabled=busy;
    button.textContent=busy?label:button.dataset.defaultLabel;
  };

  const formatDate=value=>{
    if(!value)return "";
    try{return new Intl.DateTimeFormat("vi-VN",{day:"2-digit",month:"2-digit",year:"numeric"}).format(new Date(value));}catch{return "";}
  };

  const imageSrc=listing=>{
    const first=[...(listing.listing_images||[])].sort((a,b)=>(a.sort_order||0)-(b.sort_order||0))[0];
    return first?.storage_path?api.imageUrl(first.storage_path):"";
  };

  const actionButton=(listing,action,label,className="")=>{
    const button=document.createElement("button");
    button.type="button";
    button.textContent=label;
    if(className)button.className=className;
    button.addEventListener("click",async()=>{
      const confirmText=action==="done"
        ?`Xác nhận căn này ${listing.listing_type==="rent"?"đã cho thuê":"đã bán"}? Tin sẽ ngừng hiển thị.`
        :action==="hide"?"Ẩn tin này khỏi sàn?":"Gửi tin này về trạng thái chờ duyệt lại?";
      if(!confirm(confirmText))return;
      buttonBusy(button,true,"Đang xử lý…");
      try{
        await account.ownerAction(listing.id,action);
        await loadDashboard();
      }catch(error){
        setStatus(error.message||"Chưa thực hiện được thao tác.","error");
        buttonBusy(button,false,"");
      }
    });
    return button;
  };

  const listingCard=listing=>{
    const article=document.createElement("article");
    article.className="member-listing";

    const media=document.createElement("div");
    media.className="member-listing__image";
    const src=imageSrc(listing);
    if(src){const img=document.createElement("img");img.src=src;img.alt="";img.loading="lazy";media.append(img);}else media.textContent="Chưa có ảnh";

    const body=document.createElement("div");
    const code=document.createElement("div");code.className="member-listing__code";code.textContent=listing.listing_code||"Tin đăng";
    const title=document.createElement("h3");title.textContent=listing.title||"Tin chưa có tiêu đề";
    const meta=document.createElement("div");meta.className="member-listing__meta";
    [listing.phase&&`${listing.phase}${listing.tower?` · ${listing.tower}`:""}`,listing.unit_type,listing.price_vnd&&api.formatCurrency(listing.price_vnd,listing.listing_type),listing.created_at&&`Đăng ${formatDate(listing.created_at)}`].filter(Boolean).forEach(text=>{const span=document.createElement("span");span.textContent=text;meta.append(span);});
    const badge=document.createElement("span");badge.className="member-badge";badge.dataset.status=listing.status||"";badge.textContent=statusLabels[listing.status]||listing.status||"Không rõ";
    body.append(code,title,meta,badge);

    const actions=document.createElement("div");actions.className="member-listing__actions";
    if(listing.status==="approved"&&listing.slug){
      const link=document.createElement("a");link.href=api.listingUrl(listing);link.textContent="Xem tin";link.className="is-primary";actions.append(link);
    }
    if(["approved","pending"].includes(listing.status))actions.append(actionButton(listing,"hide","Ẩn tin"));
    if(["expired","rejected","sold","rented"].includes(listing.status))actions.append(actionButton(listing,"relist","Đăng lại","is-primary"));
    if(["approved","pending"].includes(listing.status))actions.append(actionButton(listing,"done",listing.listing_type==="rent"?"Đã cho thuê":"Đã bán","is-danger"));

    article.append(media,body,actions);
    return article;
  };

  const renderListings=rows=>{
    if(!list)return;
    list.replaceChildren();
    if(!rows.length){
      const empty=document.createElement("div");empty.className="member-empty";
      const h=document.createElement("h3");h.textContent="Chưa có tin nào trong tài khoản";
      const p=document.createElement("p");p.textContent="Đăng căn khi đang đăng nhập, tin sẽ tự xuất hiện tại đây.";
      const a=document.createElement("a");a.className="btn btn-primary";a.href="/dang-tin-smart-city/";a.textContent="Đăng tin đầu tiên";
      empty.append(h,p,a);list.append(empty);return;
    }
    rows.forEach(row=>list.append(listingCard(row)));
  };

  const updateCounts=rows=>{
    const active=rows.filter(row=>row.status==="approved").length;
    const pending=rows.filter(row=>row.status==="pending").length;
    const hidden=rows.filter(row=>["expired","rejected","sold","rented"].includes(row.status)).length;
    if(counts.all)counts.all.textContent=rows.length;
    if(counts.approved)counts.approved.textContent=active;
    if(counts.pending)counts.pending.textContent=pending;
    if(counts.hidden)counts.hidden.textContent=hidden;
  };

  const showDashboard=session=>{
    if(authCard)authCard.hidden=true;
    if(dashboard)dashboard.hidden=false;
    if(identity){
      identity.replaceChildren();
      const strong=document.createElement("strong");strong.textContent="Tài khoản người đăng";
      const span=document.createElement("span");span.textContent=session?.user?.email||"Đã đăng nhập";
      identity.append(strong,span);
    }
  };

  const showAuth=()=>{
    if(authCard)authCard.hidden=false;
    if(dashboard)dashboard.hidden=true;
    setMode("signin");
  };

  async function loadDashboard(){
    const session=await account.validSession();
    if(!session){showAuth();return;}
    showDashboard(session);
    if(list){list.replaceChildren();const loading=document.createElement("div");loading.className="member-empty";loading.textContent="Đang tải tin của bạn…";list.append(loading);}
    try{
      const rows=await account.listMine();
      updateCounts(rows);renderListings(rows);setStatus("");
    }catch(error){
      renderListings([]);setStatus(error.message||"Chưa tải được danh sách tin.","error");
    }
  }

  forms.forEach(form=>form.addEventListener("submit",async event=>{
    event.preventDefault();
    setStatus("");
    const mode=form.dataset.memberForm;
    const button=form.querySelector('[type="submit"]');
    const email=form.elements.email?.value||"";
    const password=form.elements.password?.value||"";
    buttonBusy(button,true,mode==="signup"?"Đang tạo tài khoản…":"Đang đăng nhập…");
    try{
      if(mode==="signup"){
        const result=await account.signUp(email,password);
        if(result?.access_token){setStatus("Tạo tài khoản thành công.","success");await loadDashboard();}
        else setStatus("Tài khoản đã được tạo. Vui lòng kiểm tra email xác nhận rồi quay lại đăng nhập.","success");
      }else{
        await account.signIn(email,password);
        await loadDashboard();
      }
    }catch(error){
      const message=error.status===400&&/invalid login/i.test(error.message||"")?"Email hoặc mật khẩu chưa đúng.":error.message;
      setStatus(message||"Chưa đăng nhập được.","error");
    }finally{buttonBusy(button,false,"");}
  }));

  document.querySelector("[data-member-signout]")?.addEventListener("click",async event=>{
    const button=event.currentTarget;button.disabled=true;
    await account.signOut();
    button.disabled=false;showAuth();
  });

  loadDashboard().catch(()=>showAuth());
})();
