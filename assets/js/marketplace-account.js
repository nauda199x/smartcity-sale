(()=>{
  "use strict";
  const api=window.SmartCityMarketplace;
  const config=window.SMARTCITY_MARKETPLACE_CONFIG||{};
  if(!api||window.SmartCityMarketplaceAccount)return;

  const base=String(config.supabaseUrl||"").replace(/\/$/,"");
  const publishableKey=String(config.supabasePublishableKey||config.supabaseAnonKey||"");
  const sessionKey="smartcity_marketplace_member_session_v1";
  const originalCreateListing=api.createListing;
  const originalUploadImage=api.uploadImage;
  const originalAddListingImage=api.addListingImage;
  let refreshInFlight=null;

  class MemberError extends Error{
    constructor(message,status=0,details=null){super(message);this.name="MemberError";this.status=status;this.details=details;}
  }

  const parseResponse=async response=>{
    if(response.status===204)return null;
    const text=await response.text();
    if(!text)return null;
    try{return JSON.parse(text);}catch{return text;}
  };

  const request=async(path,{method="GET",body,token,headers={}}={})=>{
    if(!base||!publishableKey)throw new MemberError("Hệ thống tài khoản chưa được kết nối.");
    const binary=body instanceof Blob||body instanceof ArrayBuffer;
    const response=await fetch(`${base}${path}`,{
      method,
      headers:{
        apikey:publishableKey,
        ...(token?{Authorization:`Bearer ${token}`}:{}) ,
        ...(body!==undefined&&!binary?{"Content-Type":"application/json"}:{}),
        ...headers
      },
      body:body===undefined?undefined:(binary?body:JSON.stringify(body))
    });
    const data=await parseResponse(response);
    if(!response.ok){
      const message=data?.msg||data?.message||data?.error_description||data?.error||`Yêu cầu không thành công (${response.status}).`;
      throw new MemberError(message,response.status,data);
    }
    return data;
  };

  const getSession=()=>{
    try{return JSON.parse(localStorage.getItem(sessionKey)||"null");}catch{return null;}
  };
  const saveSession=session=>{
    try{
      if(session){
        localStorage.setItem(sessionKey,JSON.stringify({
          ...session,
          expires_at:session.expires_at||(Math.floor(Date.now()/1000)+Number(session.expires_in||3600))
        }));
      }else localStorage.removeItem(sessionKey);
    }catch{}
  };

  const refreshSession=async session=>{
    if(!session?.refresh_token)return null;
    if(refreshInFlight)return refreshInFlight;
    refreshInFlight=(async()=>{
      try{
        const refreshed=await request("/auth/v1/token?grant_type=refresh_token",{
          method:"POST",body:{refresh_token:session.refresh_token}
        });
        saveSession(refreshed);
        return refreshed;
      }catch{
        saveSession(null);
        return null;
      }
    })();
    try{return await refreshInFlight;}finally{refreshInFlight=null;}
  };

  const validSession=async()=>{
    let session=getSession();
    if(!session?.access_token)return null;
    const expiresAt=Number(session.expires_at||0);
    if(expiresAt&&expiresAt-Date.now()/1000<90)session=await refreshSession(session);
    if(!session?.access_token)return null;
    if(!session.user?.id){
      try{
        const user=await request("/auth/v1/user",{token:session.access_token});
        session={...session,user};saveSession(session);
      }catch{return null;}
    }
    return session;
  };

  const signUp=async(email,password)=>{
    const normalized=api.cleanText(email,200).toLowerCase();
    if(!/^\S+@\S+\.\S+$/.test(normalized))throw new MemberError("Email chưa đúng định dạng.",400);
    if(String(password||"").length<8)throw new MemberError("Mật khẩu cần ít nhất 8 ký tự.",400);
    const result=await request("/auth/v1/signup",{method:"POST",body:{email:normalized,password:String(password)}});
    if(result?.access_token)saveSession(result);
    return result;
  };

  const signIn=async(email,password)=>{
    const normalized=api.cleanText(email,200).toLowerCase();
    const session=await request("/auth/v1/token?grant_type=password",{
      method:"POST",body:{email:normalized,password:String(password||"")}
    });
    saveSession(session);
    return session;
  };

  const signOut=async()=>{
    const session=getSession();
    if(session?.access_token){
      try{await request("/auth/v1/logout",{method:"POST",token:session.access_token});}catch{}
    }
    saveSession(null);
  };

  const restPath=(table,params={})=>{
    const search=new URLSearchParams(params);
    return `/rest/v1/${table}${search.size?`?${search.toString()}`:""}`;
  };

  const listMine=async()=>{
    const session=await validSession();
    if(!session)throw new MemberError("Vui lòng đăng nhập để xem tin của bạn.",401);
    return request(restPath("listings",{
      select:"id,listing_code,slug,listing_type,status,title,phase,tower,unit_type,area_sqm,price_vnd,poster_type,created_at,updated_at,approved_at,expires_at,listing_images(storage_path,sort_order,alt_text)",
      owner_user_id:`eq.${session.user.id}`,
      order:"created_at.desc",
      limit:"300",
      "listing_images.order":"sort_order.asc,id.asc",
      "listing_images.limit":"1"
    }),{token:session.access_token});
  };

  const ownerAction=async(listingId,action)=>{
    const session=await validSession();
    if(!session)throw new MemberError("Phiên đăng nhập đã hết hạn.",401);
    if(!["hide","relist","done"].includes(action))throw new MemberError("Thao tác không hợp lệ.",400);
    return request("/rest/v1/rpc/owner_listing_action",{
      method:"POST",token:session.access_token,body:{p_listing_id:listingId,p_action:action}
    });
  };

  // When a member is signed in, keep the existing zero-friction form but bind the
  // new listing and image uploads to that member. Anonymous behavior is unchanged.
  api.createListing=async data=>{
    const session=await validSession();
    if(!session)return originalCreateListing(data);
    const id=crypto.randomUUID();
    const listingCode=`SC-${crypto.randomUUID().replace(/-/g,"").slice(0,8).toUpperCase()}`;
    const slug=`${api.slugify(data.title)||"tin-dang-smart-city"}-${listingCode.toLowerCase()}`;
    const posterType=document.querySelector('[name="poster_type"]:checked')?.value;
    const payload={...data,id,listing_code:listingCode,slug,owner_user_id:session.user.id,...(["owner","agent"].includes(posterType)?{poster_type:posterType}:{})};
    await request(restPath("listings"),{
      method:"POST",token:session.access_token,body:payload,headers:{Prefer:"return=minimal"}
    });
    return {...payload,status:"pending",is_featured:false,sort_priority:0};
  };

  api.uploadImage=async(listingId,file,index)=>{
    const session=await validSession();
    if(!session)return originalUploadImage(listingId,file,index);
    const extension=(file.name.split(".").pop()||"jpg").toLowerCase().replace(/[^a-z0-9]/g,"").slice(0,5)||"jpg";
    const path=`pending/${listingId}/${String(index+1).padStart(2,"0")}-${crypto.randomUUID()}.${extension}`;
    const encoded=path.split("/").map(encodeURIComponent).join("/");
    await request(`/storage/v1/object/${encodeURIComponent(config.storageBucket||"listing-images")}/${encoded}`,{
      method:"POST",token:session.access_token,body:file,headers:{"Content-Type":file.type,"x-upsert":"false"}
    });
    return path;
  };

  api.addListingImage=async(listingId,path,index,altText)=>{
    const session=await validSession();
    if(!session)return originalAddListingImage(listingId,path,index,altText);
    return request(restPath("listing_images"),{
      method:"POST",token:session.access_token,
      body:{listing_id:listingId,storage_path:path,sort_order:index,alt_text:api.cleanText(altText,180)},
      headers:{Prefer:"return=minimal"}
    });
  };

  const injectPosterType=()=>{
    const step=document.querySelector('[data-form-step="4"]');
    if(!step||step.querySelector('[name="poster_type"]'))return;
    const row=step.querySelector(".field-row");
    if(!row)return;
    const fieldset=document.createElement("fieldset");
    fieldset.className="member-poster-type";
    fieldset.innerHTML=`<legend>Bạn đăng với vai trò nào?</legend>
      <label><input type="radio" name="poster_type" value="owner" checked><span><strong>Chủ nhà</strong><small>Căn thuộc quỹ của bạn</small></span></label>
      <label><input type="radio" name="poster_type" value="agent"><span><strong>Môi giới</strong><small>Đăng nguồn hàng đang phụ trách</small></span></label>`;
    row.before(fieldset);
  };

  const injectAccountPrompt=async()=>{
    const head=document.querySelector(".post-form-head");
    if(!head||document.querySelector("[data-member-post-prompt]"))return;
    const session=await validSession();
    const box=document.createElement("div");
    box.className="member-post-prompt";
    box.dataset.memberPostPrompt="";
    const mark=document.createElement("span");
    mark.className="member-post-prompt__mark";
    mark.setAttribute("aria-hidden","true");
    const copy=document.createElement("div");
    const strong=document.createElement("strong");
    const paragraph=document.createElement("p");
    const link=document.createElement("a");
    link.href="/tai-khoan-smart-city/";
    if(session){
      mark.textContent="✓";
      strong.textContent=`Đang đăng bằng tài khoản ${session.user?.email||""}`;
      paragraph.textContent="Tin gửi từ form này sẽ tự xuất hiện trong mục “Tin của tôi” để bạn theo dõi, ẩn hoặc đăng lại.";
      link.textContent="Tin của tôi →";
    }else{
      mark.textContent="◎";
      strong.textContent="Đăng nhanh vẫn không cần tài khoản.";
      paragraph.textContent="Nếu thường xuyên đăng nhiều căn, bạn có thể tạo tài khoản để quản lý toàn bộ tin trên một màn hình.";
      link.textContent="Đăng nhập / tạo tài khoản →";
    }
    copy.append(strong,paragraph);box.append(mark,copy,link);head.after(box);
  };

  const bootPostingEnhancements=()=>{
    if(!document.querySelector("[data-marketplace-submit]"))return;
    injectPosterType();
    injectAccountPrompt().catch(()=>{});
  };

  window.SmartCityMarketplaceAccount={
    MemberError,getSession,validSession,signUp,signIn,signOut,listMine,ownerAction
  };

  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",bootPostingEnhancements,{once:true});
  else bootPostingEnhancements();
})();
