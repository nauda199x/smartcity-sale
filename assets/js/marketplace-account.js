(()=>{
  "use strict";
  const config=window.SMARTCITY_MARKETPLACE_CONFIG||{};
  const api=window.SmartCityMarketplace||null;
  const base=String(config.supabaseUrl||"").replace(/\/$/,"");
  const key=String(config.supabasePublishableKey||config.supabaseAnonKey||"");
  const sessionKey="smartcity_marketplace_user_session";
  const pendingProfileKey="smartcity_marketplace_pending_profile";
  const configured=()=>Boolean(base&&key&&!base.includes("YOUR_PROJECT"));
  const clean=(value,max=300)=>String(value??"").trim().slice(0,max);
  const escapeHtml=(value,max=500)=>clean(value,max).replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const safeStatus=value=>clean(value,24).toLowerCase().replace(/[^a-z-]/g,"");

  const headers=token=>({apikey:key,...(token?{Authorization:`Bearer ${token}`}:{})});
  const parse=async response=>{
    if(response.status===204)return null;
    const text=await response.text();
    if(!text)return null;
    try{return JSON.parse(text);}catch{return text;}
  };
  const request=async(path,{method="GET",body,token,prefer}={})=>{
    if(!configured())throw new Error("Hệ thống tài khoản chưa được kết nối.");
    const response=await fetch(`${base}${path}`,{
      method,
      headers:{...headers(token),...(body!==undefined?{"Content-Type":"application/json"}:{}),...(prefer?{Prefer:prefer}:{})},
      body:body===undefined?undefined:JSON.stringify(body)
    });
    const data=await parse(response);
    if(!response.ok){
      const message=data?.msg||data?.message||data?.error_description||data?.error||`Yêu cầu không thành công (${response.status}).`;
      const error=new Error(message);error.status=response.status;error.details=data;throw error;
    }
    return data;
  };

  const readSession=()=>{try{return JSON.parse(localStorage.getItem(sessionKey)||"null");}catch{return null;}};
  const saveSession=session=>{
    if(session){
      const expiresAt=Number(session.expires_at||0)||(Math.floor(Date.now()/1000)+Number(session.expires_in||3600));
      localStorage.setItem(sessionKey,JSON.stringify({...session,expires_at:expiresAt}));
    }else localStorage.removeItem(sessionKey);
  };
  let refreshPromise=null;
  const refresh=async session=>{
    if(!session?.refresh_token)return null;
    if(refreshPromise)return refreshPromise;
    refreshPromise=(async()=>{try{
      const next=await request("/auth/v1/token?grant_type=refresh_token",{method:"POST",body:{refresh_token:session.refresh_token}});
      saveSession(next);return next;
    }catch{saveSession(null);return null;}})();
    try{return await refreshPromise;}finally{refreshPromise=null;}
  };
  const currentSession=async()=>{
    let session=readSession();
    if(!session)return null;
    if(Number(session.expires_at||0)-Date.now()/1000<90)session=await refresh(session);
    return session;
  };
  const currentUser=async()=>{
    const session=await currentSession();
    if(!session?.access_token)return null;
    if(session.user?.id)return session.user;
    try{
      const user=await request("/auth/v1/user",{token:session.access_token});
      saveSession({...session,user});return user;
    }catch{saveSession(null);return null;}
  };

  const signIn=async(email,password)=>{
    const session=await request("/auth/v1/token?grant_type=password",{method:"POST",body:{email:clean(email,200),password:String(password||"")}});
    saveSession(session);
    await applyPendingProfile();
    return session;
  };
  const signUp=async({email,password,displayName,phone,posterType,companyName})=>{
    const profile={displayName:clean(displayName,120),phone:clean(phone,30),posterType:posterType==="owner"?"owner":"agent",companyName:clean(companyName,160)};
    localStorage.setItem(pendingProfileKey,JSON.stringify(profile));
    const result=await request("/auth/v1/signup",{method:"POST",body:{
      email:clean(email,200),password:String(password||""),data:{display_name:profile.displayName,phone:profile.phone,poster_type:profile.posterType,company_name:profile.companyName}
    }});
    if(result?.access_token){saveSession(result);await applyPendingProfile();}
    return result;
  };
  const signOut=async()=>{
    const session=readSession();
    if(session?.access_token){try{await request("/auth/v1/logout",{method:"POST",token:session.access_token});}catch{}}
    saveSession(null);
  };

  const upsertProfile=async profile=>{
    const session=await currentSession();
    if(!session?.access_token)throw new Error("Vui lòng đăng nhập để lưu hồ sơ.");
    return request("/rest/v1/rpc/marketplace_upsert_profile",{method:"POST",token:session.access_token,body:{
      p_display_name:clean(profile.displayName,120),p_phone:clean(profile.phone,30),p_poster_type:profile.posterType==="owner"?"owner":"agent",p_company_name:clean(profile.companyName,160)||null
    }});
  };
  const applyPendingProfile=async()=>{
    let pending=null;
    try{pending=JSON.parse(localStorage.getItem(pendingProfileKey)||"null");}catch{}
    if(!pending)return null;
    try{const saved=await upsertProfile(pending);localStorage.removeItem(pendingProfileKey);return saved;}catch{return null;}
  };
  const getProfile=async()=>{
    const session=await currentSession();const user=session?.user||await currentUser();
    if(!session?.access_token||!user?.id)return null;
    const rows=await request(`/rest/v1/marketplace_profiles?select=user_id,display_name,phone,poster_type,company_name,is_verified,created_at,updated_at&user_id=eq.${encodeURIComponent(user.id)}&limit=1`,{token:session.access_token});
    return rows?.[0]||null;
  };

  const listMyListings=async()=>{
    const session=await currentSession();const user=session?.user||await currentUser();
    if(!session?.access_token||!user?.id)throw new Error("Vui lòng đăng nhập.");
    const select="id,slug,listing_code,listing_type,status,title,phase,tower,unit_type,area_sqm,price_vnd,poster_name,contact_phone,is_featured,approved_at,expires_at,created_at,updated_at,view_count,listing_images(storage_path,sort_order,alt_text)";
    return request(`/rest/v1/listings?select=${encodeURIComponent(select)}&owner_user_id=eq.${encodeURIComponent(user.id)}&order=created_at.desc&limit=200`,{token:session.access_token});
  };
  const listingAction=async(id,action)=>{
    const session=await currentSession();
    if(!session?.access_token)throw new Error("Vui lòng đăng nhập lại.");
    return request("/rest/v1/rpc/marketplace_my_listing_action",{method:"POST",token:session.access_token,body:{p_listing_id:id,p_action:action}});
  };

  const ownedCreateListing=async data=>{
    const session=await currentSession();
    if(!session?.access_token||!session?.user?.id)return null;
    const id=crypto.randomUUID();
    const code=`SC-${crypto.randomUUID().replace(/-/g,"").slice(0,8).toUpperCase()}`;
    const slugBase=api?.slugify?api.slugify(data.title):clean(data.title,120).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/đ/g,"d").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,90);
    const payload={...data,id,listing_code:code,slug:`${slugBase||"tin-dang-smart-city"}-${code.toLowerCase()}`,owner_user_id:session.user.id};
    await request("/rest/v1/listings",{method:"POST",token:session.access_token,body:payload,prefer:"return=minimal"});
    return {...payload,status:"pending",is_featured:false,sort_priority:0};
  };

  if(api&&!api.__posterAccountsPatched){
    const anonymousCreate=api.createListing.bind(api);
    api.createListing=async data=>{
      try{
        const owned=await ownedCreateListing(data);
        if(owned)return owned;
      }catch(error){
        if(await currentSession())throw error;
      }
      return anonymousCreate(data);
    };
    Object.defineProperty(api,"__posterAccountsPatched",{value:true});
  }

  const statusLabel=status=>({pending:"Chờ duyệt",approved:"Đang hiển thị",expired:"Đã ẩn / hết hạn",rejected:"Không duyệt",sold:"Đã bán",rented:"Đã cho thuê"}[status]||status||"—");
  const formatDate=value=>value?new Intl.DateTimeFormat("vi-VN",{day:"2-digit",month:"2-digit",year:"numeric"}).format(new Date(value)):"—";
  const money=row=>api?.formatCurrency?api.formatCurrency(row.price_vnd,row.listing_type):new Intl.NumberFormat("vi-VN").format(Number(row.price_vnd||0));
  const listingHref=row=>api?.listingUrl?api.listingUrl(row):`/${row.listing_type==="rent"?"cho-thue-smart-city":"mua-ban-smart-city"}/${encodeURIComponent(row.slug||"")}/`;

  const prefillPosting=async()=>{
    const form=document.querySelector("[data-marketplace-submit]");
    if(!form)return;
    const session=await currentSession();
    if(!session?.access_token)return;
    const profile=await getProfile().catch(()=>null);
    if(profile){
      const name=form.elements.poster_name,phone=form.elements.contact_phone;
      if(name&&!name.value)name.value=profile.display_name||"";
      if(phone&&!phone.value)phone.value=profile.phone||"";
      name?.dispatchEvent(new Event("input",{bubbles:true}));phone?.dispatchEvent(new Event("input",{bubbles:true}));
    }
    if(form.parentElement&&!document.querySelector("[data-account-posting-note]")){
      const box=document.createElement("div");box.className="account-posting-note";box.dataset.accountPostingNote="";
      box.innerHTML=`<div><strong>Đang đăng bằng tài khoản của bạn</strong><span>Tin mới sẽ tự xuất hiện trong mục “Tin của tôi” để theo dõi lượt xem và trạng thái duyệt.</span></div><a href="/tai-khoan-smart-city/">Tin của tôi →</a>`;
      form.insertAdjacentElement("beforebegin",box);
    }
  };

  const initAccountPage=async()=>{
    const root=document.querySelector("[data-account-root]");if(!root)return;
    const authView=root.querySelector("[data-account-auth]");
    const dashboard=root.querySelector("[data-account-dashboard]");
    const notice=root.querySelector("[data-account-notice]");
    const showNotice=(message,type="")=>{notice.hidden=false;notice.textContent=message;notice.className=`account-notice${type?` is-${type}`:""}`;};
    const clearNotice=()=>{notice.hidden=true;notice.textContent="";notice.className="account-notice";};

    const renderDashboard=async()=>{
      clearNotice();
      const session=await currentSession();
      if(!session?.access_token){authView.hidden=false;dashboard.hidden=true;return;}
      await applyPendingProfile();
      authView.hidden=true;dashboard.hidden=false;
      const profile=await getProfile().catch(()=>null);
      const user=await currentUser();
      root.querySelector("[data-account-name]").textContent=profile?.display_name||user?.email||"Tài khoản";
      root.querySelector("[data-account-email]").textContent=user?.email||"";
      root.querySelector("[data-account-profile-badge]").textContent=profile?.is_verified?"Đã xác minh":"Tài khoản thường";
      const form=root.querySelector("[data-profile-form]");
      if(form&&profile){form.elements.display_name.value=profile.display_name||"";form.elements.phone.value=profile.phone||"";form.elements.poster_type.value=profile.poster_type||"agent";form.elements.company_name.value=profile.company_name||"";}

      const list=root.querySelector("[data-my-listings]");
      list.innerHTML='<div class="account-loading">Đang tải tin của bạn…</div>';
      let rows=[];
      try{rows=await listMyListings();}catch(error){list.innerHTML="";showNotice(error.message,"error");return;}
      const counts={all:rows.length,pending:0,approved:0,done:0};
      rows.forEach(row=>{if(row.status==="pending")counts.pending++;if(row.status==="approved")counts.approved++;if(["sold","rented","expired","rejected"].includes(row.status))counts.done++;});
      root.querySelector("[data-count-all]").textContent=counts.all;
      root.querySelector("[data-count-pending]").textContent=counts.pending;
      root.querySelector("[data-count-approved]").textContent=counts.approved;
      root.querySelector("[data-count-views]").textContent=rows.reduce((sum,row)=>sum+Number(row.view_count||0),0);
      if(!rows.length){list.innerHTML='<div class="account-empty"><strong>Chưa có tin nào gắn với tài khoản này.</strong><p>Đăng tin mới khi đang đăng nhập, tin sẽ tự xuất hiện tại đây.</p><a class="btn btn-primary" href="/dang-tin-smart-city/">Đăng tin đầu tiên</a></div>';return;}
      list.replaceChildren(...rows.map(row=>{
        const image=[...(row.listing_images||[])].sort((a,b)=>Number(a.sort_order||0)-Number(b.sort_order||0))[0];
        const card=document.createElement("article");card.className="account-listing-card";card.dataset.listingId=clean(row.id,50);
        const img=image&&api?.imageUrl?api.imageUrl(image.storage_path):"";
        const publicLink=row.status==="approved"?`<a class="account-card-link" href="${escapeHtml(listingHref(row),300)}">Xem tin →</a>`:"";
        const actionButtons=[];
        if(["pending","approved"].includes(row.status))actionButtons.push('<button type="button" data-my-action="hide">Ẩn tin</button>');
        if(row.status==="approved")actionButtons.push(`<button type="button" data-my-action="done">${row.listing_type==="rent"?"Đã cho thuê":"Đã bán"}</button>`);
        if(["expired","rejected","sold","rented"].includes(row.status))actionButtons.push('<button type="button" data-my-action="renew">Đăng lại / chờ duyệt</button>');
        card.innerHTML=`${img?`<img src="${escapeHtml(img,900)}" alt="" loading="lazy" decoding="async">`:'<div class="account-card-placeholder">SC</div>'}<div class="account-card-body"><div class="account-card-top"><span class="account-status is-${safeStatus(row.status)}">${escapeHtml(statusLabel(row.status),60)}</span><small>${escapeHtml(row.listing_code,30)}</small></div><h3>${escapeHtml(row.title,180)}</h3><p class="account-card-location">${escapeHtml(row.phase,60)} · ${escapeHtml(row.tower,40)} · ${escapeHtml(row.unit_type,50)}</p><div class="account-card-facts"><strong>${escapeHtml(money(row),60)}</strong><span>${Number(row.view_count||0).toLocaleString("vi-VN")} lượt xem</span><span>Đăng ${escapeHtml(formatDate(row.created_at),30)}</span></div><div class="account-card-actions">${publicLink}${actionButtons.join("")}</div></div>`;
        return card;
      }));
    };

    root.querySelector("[data-login-form]")?.addEventListener("submit",async event=>{
      event.preventDefault();clearNotice();const form=event.currentTarget;const button=form.querySelector('button[type="submit"]');button.disabled=true;button.textContent="Đang đăng nhập…";
      try{await signIn(form.elements.email.value,form.elements.password.value);await renderDashboard();}
      catch(error){showNotice(error.message.includes("Invalid login")?"Email hoặc mật khẩu chưa đúng.":error.message,"error");}
      finally{button.disabled=false;button.textContent="Đăng nhập";}
    });
    root.querySelector("[data-register-form]")?.addEventListener("submit",async event=>{
      event.preventDefault();clearNotice();const form=event.currentTarget;const button=form.querySelector('button[type="submit"]');
      if(String(form.elements.password.value||"").length<8){showNotice("Mật khẩu cần ít nhất 8 ký tự.","error");return;}
      button.disabled=true;button.textContent="Đang tạo tài khoản…";
      try{
        const result=await signUp({email:form.elements.email.value,password:form.elements.password.value,displayName:form.elements.display_name.value,phone:form.elements.phone.value,posterType:form.elements.poster_type.value,companyName:form.elements.company_name.value});
        if(result?.access_token){await renderDashboard();showNotice("Tạo tài khoản thành công. Từ giờ tin mới sẽ được quản lý trong tài khoản này.","success");}
        else showNotice("Tài khoản đã được tạo. Hãy kiểm tra email xác nhận, sau đó quay lại đăng nhập.","success");
      }catch(error){showNotice(error.message,"error");}
      finally{button.disabled=false;button.textContent="Tạo tài khoản";}
    });
    root.querySelector("[data-profile-form]")?.addEventListener("submit",async event=>{
      event.preventDefault();clearNotice();const form=event.currentTarget;const button=form.querySelector('button[type="submit"]');button.disabled=true;
      try{await upsertProfile({displayName:form.elements.display_name.value,phone:form.elements.phone.value,posterType:form.elements.poster_type.value,companyName:form.elements.company_name.value});showNotice("Đã cập nhật hồ sơ.","success");await renderDashboard();}
      catch(error){showNotice(error.message,"error");}
      finally{button.disabled=false;}
    });
    root.querySelector("[data-account-signout]")?.addEventListener("click",async()=>{await signOut();location.reload();});
    root.querySelector("[data-my-listings]")?.addEventListener("click",async event=>{
      const button=event.target.closest("[data-my-action]");if(!button)return;
      const card=button.closest("[data-listing-id]");if(!card)return;
      const action=button.dataset.myAction;
      const question=action==="hide"?"Ẩn tin này khỏi sàn?":action==="done"?"Đánh dấu giao dịch đã hoàn tất?":"Đưa tin này về chờ duyệt để đăng lại?";
      if(!confirm(question))return;
      button.disabled=true;const before=button.textContent;button.textContent="Đang xử lý…";
      try{await listingAction(card.dataset.listingId,action);showNotice("Đã cập nhật trạng thái tin.","success");await renderDashboard();}
      catch(error){showNotice(error.message,"error");button.disabled=false;button.textContent=before;}
    });
    root.querySelectorAll("[data-auth-tab]").forEach(button=>button.addEventListener("click",()=>{
      const tab=button.dataset.authTab;root.querySelectorAll("[data-auth-tab]").forEach(item=>item.classList.toggle("is-active",item===button));
      root.querySelector("[data-login-form]").hidden=tab!=="login";root.querySelector("[data-register-form]").hidden=tab!=="register";
    }));
    await renderDashboard();
  };

  window.SmartCityAccount={currentSession,currentUser,signIn,signUp,signOut,getProfile,upsertProfile,listMyListings,listingAction};
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",()=>{prefillPosting();initAccountPage();},{once:true});
  else{prefillPosting();initAccountPage();}
})();