(()=>{
  "use strict";
  if(window.SmartCitySavedSearches)return;

  const config=window.SMARTCITY_MARKETPLACE_CONFIG||{};
  const base=String(config.supabaseUrl||"").replace(/\/$/,"");
  const key=String(config.supabasePublishableKey||config.supabaseAnonKey||"");
  const pendingKey="smartcity_marketplace_pending_saved_search_v1";

  class SavedSearchError extends Error{
    constructor(message,status=0,details=null){super(message);this.name="SavedSearchError";this.status=status;this.details=details;}
  }

  const clean=(value,max=160)=>String(value??"").trim().slice(0,max);
  const parse=async response=>{
    if(response.status===204||response.status===205)return null;
    const text=await response.text();
    if(!text)return null;
    try{return JSON.parse(text);}catch{return text;}
  };
  const session=async()=>{
    const account=window.SmartCityMarketplaceAccount;
    if(!account?.validSession)return null;
    return account.validSession();
  };
  const request=async(path,{method="GET",body,token,headers={}}={})=>{
    if(!base||!key)throw new SavedSearchError("Hệ thống lưu tìm kiếm chưa được kết nối.");
    const response=await fetch(`${base}${path}`,{
      method,
      headers:{
        apikey:key,
        ...(token?{Authorization:`Bearer ${token}`}:{}) ,
        ...(body!==undefined?{"Content-Type":"application/json"}:{}),
        ...headers
      },
      body:body===undefined?undefined:JSON.stringify(body)
    });
    const data=await parse(response);
    if(!response.ok){
      const message=data?.message||data?.msg||data?.error_description||data?.error||`Yêu cầu không thành công (${response.status}).`;
      throw new SavedSearchError(message,response.status,data);
    }
    return data;
  };

  const areaBounds=value=>{
    const raw=clean(value,30);
    if(!raw)return {min:null,max:null};
    if(raw==="120-9999")return {min:120,max:null};
    const [a,b]=raw.split("-").map(Number);
    if(!Number.isFinite(a)||!Number.isFinite(b))return {min:null,max:null};
    return {min:a,max:b};
  };
  const areaKey=search=>{
    const min=search.min_area_sqm===null||search.min_area_sqm===undefined?null:Number(search.min_area_sqm);
    const max=search.max_area_sqm===null||search.max_area_sqm===undefined?null:Number(search.max_area_sqm);
    if(min===120&&max===null)return "120-9999";
    const known=[[0,50,"0-50"],[50,70,"50-70"],[70,90,"70-90"],[90,120,"90-120"]];
    return known.find(([a,b])=>min===a&&max===b)?.[2]||"";
  };
  const numberOrNull=value=>{
    const number=Number(value);
    return value!==""&&value!==null&&value!==undefined&&Number.isFinite(number)&&number>0?Math.round(number):null;
  };

  const normalize=criteria=>{
    const bounds=areaBounds(criteria.area);
    return {
      listing_type:criteria.listing_type==="rent"?"rent":"sale",
      keyword:clean(criteria.keyword,100)||null,
      phase:clean(criteria.phase,80)||null,
      tower:clean(criteria.tower,80)||null,
      unit_type:clean(criteria.bedroom||criteria.unit_type,80)||null,
      min_price_vnd:numberOrNull(criteria.min_price||criteria.minPrice),
      max_price_vnd:numberOrNull(criteria.max_price||criteria.maxPrice),
      min_area_sqm:bounds.min,
      max_area_sqm:bounds.max,
      furnishing:clean(criteria.furnishing,80)||null,
    };
  };

  const shortPrice=(value,type)=>{
    const amount=Number(value||0);
    if(!amount)return "";
    if(type==="rent")return `${new Intl.NumberFormat("vi-VN",{maximumFractionDigits:1}).format(amount/1e6)}tr`;
    return `${new Intl.NumberFormat("vi-VN",{maximumFractionDigits:1}).format(amount/1e9)}tỷ`;
  };
  const labelFor=search=>{
    const action=search.listing_type==="rent"?"Thuê":"Mua";
    const bits=[action,search.phase,search.tower,search.unit_type].filter(Boolean);
    if(search.min_price_vnd&&search.max_price_vnd)bits.push(`${shortPrice(search.min_price_vnd,search.listing_type)}–${shortPrice(search.max_price_vnd,search.listing_type)}`);
    else if(search.max_price_vnd)bits.push(`≤ ${shortPrice(search.max_price_vnd,search.listing_type)}`);
    else if(search.min_price_vnd)bits.push(`≥ ${shortPrice(search.min_price_vnd,search.listing_type)}`);
    const area=areaKey(search);
    if(area)bits.push(area==="120-9999"?">120m²":`${area}m²`);
    if(search.keyword)bits.push(`“${search.keyword}”`);
    return clean(bits.join(" · ")||`${action} căn hộ Smart City`,120);
  };

  const fingerprintFor=async search=>{
    const canonical=[
      search.listing_type,search.keyword||"",search.phase||"",search.tower||"",search.unit_type||"",
      search.min_price_vnd||"",search.max_price_vnd||"",search.min_area_sqm??"",search.max_area_sqm??"",search.furnishing||""
    ].map(value=>String(value).trim().toLocaleLowerCase("vi")).join("|");
    if(globalThis.crypto?.subtle){
      const digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(canonical));
      return `v1-${[...new Uint8Array(digest)].map(byte=>byte.toString(16).padStart(2,"0")).join("")}`;
    }
    let hash=2166136261;
    for(let i=0;i<canonical.length;i++){hash^=canonical.charCodeAt(i);hash=Math.imul(hash,16777619);}
    return `v1-fnv-${(hash>>>0).toString(16).padStart(8,"0")}`;
  };

  const list=async()=>{
    const s=await session();
    if(!s)throw new SavedSearchError("Vui lòng đăng nhập để xem tìm kiếm đã lưu.",401);
    const params=new URLSearchParams({
      select:"id,label,listing_type,keyword,phase,tower,unit_type,min_price_vnd,max_price_vnd,min_area_sqm,max_area_sqm,furnishing,fingerprint,last_seen_at,is_active,created_at,updated_at",
      user_id:`eq.${s.user.id}`,
      is_active:"eq.true",
      order:"updated_at.desc",
      limit:"30"
    });
    return request(`/rest/v1/saved_searches?${params}`,{token:s.access_token});
  };

  const save=async criteria=>{
    const s=await session();
    if(!s)throw new SavedSearchError("Vui lòng đăng nhập để lưu tìm kiếm.",401);
    const search=normalize(criteria);
    const fingerprint=await fingerprintFor(search);
    const now=new Date().toISOString();
    const payload={...search,user_id:s.user.id,fingerprint,label:labelFor(search),last_seen_at:now,is_active:true,updated_at:now};
    const params=new URLSearchParams({on_conflict:"user_id,fingerprint"});
    const rows=await request(`/rest/v1/saved_searches?${params}`,{
      method:"POST",token:s.access_token,body:payload,
      headers:{Prefer:"resolution=merge-duplicates,return=representation"}
    });
    return rows?.[0]||payload;
  };

  const remove=async id=>{
    const s=await session();
    if(!s)throw new SavedSearchError("Phiên đăng nhập đã hết hạn.",401);
    await request(`/rest/v1/saved_searches?id=eq.${encodeURIComponent(id)}&user_id=eq.${encodeURIComponent(s.user.id)}`,{
      method:"DELETE",token:s.access_token,headers:{Prefer:"return=minimal"}
    });
  };

  const touch=async id=>{
    const s=await session();
    if(!s)throw new SavedSearchError("Phiên đăng nhập đã hết hạn.",401);
    const now=new Date().toISOString();
    await request(`/rest/v1/saved_searches?id=eq.${encodeURIComponent(id)}&user_id=eq.${encodeURIComponent(s.user.id)}`,{
      method:"PATCH",token:s.access_token,body:{last_seen_at:now,updated_at:now},headers:{Prefer:"return=minimal"}
    });
    return now;
  };

  const unitFilter=value=>{
    const aliases={"1PN+1":["1PN+1","1PN+"],"2PN+1":["2PN+1","2PN+","2PN+1 (1WC)","2PN+1 (2WC)"],"3PN+1":["3PN+1","3PN+"]};
    return aliases[value]?`in.(${aliases[value].map(item=>JSON.stringify(item)).join(",")})`:`eq.${value}`;
  };
  const matchParams=(search,newOnly=true)=>{
    const params=new URLSearchParams({select:"id",status:"eq.approved",listing_type:`eq.${search.listing_type==="rent"?"rent":"sale"}`});
    if(search.phase)params.set("phase",`eq.${search.phase}`);
    if(search.tower)params.set("tower",`eq.${search.tower}`);
    if(search.unit_type)params.set("unit_type",unitFilter(search.unit_type));
    if(search.furnishing)params.set("furnishing",`eq.${search.furnishing}`);
    const ranges=[];
    if(Number(search.min_price_vnd)>0)ranges.push(`price_vnd.gte.${Number(search.min_price_vnd)}`);
    if(Number(search.max_price_vnd)>0)ranges.push(`price_vnd.lte.${Number(search.max_price_vnd)}`);
    if(search.min_area_sqm!==null&&search.min_area_sqm!==undefined)ranges.push(`area_sqm.gte.${Number(search.min_area_sqm)}`);
    if(search.max_area_sqm!==null&&search.max_area_sqm!==undefined)ranges.push(`area_sqm.lte.${Number(search.max_area_sqm)}`);
    if(ranges.length)params.set("and",`(${ranges.join(",")})`);
    if(search.keyword){
      const literal=String(search.keyword).replace(/[\\%_*]/g,"\\$&");
      const value=JSON.stringify(`%${literal}%`);
      params.set("or",`(${["title","phase","tower","unit_type"].map(field=>`${field}.ilike.${value}`).join(",")})`);
    }
    if(newOnly&&search.last_seen_at)params.set("approved_at",`gt.${search.last_seen_at}`);
    return params;
  };

  const countMatches=async(search,{newOnly=true}={})=>{
    const s=await session();
    if(!s)throw new SavedSearchError("Phiên đăng nhập đã hết hạn.",401);
    const response=await fetch(`${base}/rest/v1/listings?${matchParams(search,newOnly)}`,{
      method:"HEAD",
      headers:{apikey:key,Authorization:`Bearer ${s.access_token}`,Prefer:"count=exact",Range:"0-0"}
    });
    if(!response.ok&&response.status!==416)throw new SavedSearchError("Chưa đếm được căn phù hợp.",response.status);
    const range=response.headers.get("Content-Range")||"";
    const total=range.split("/")[1];
    return /^\d+$/.test(total||"")?Number(total):0;
  };

  const urlFor=search=>{
    const segment=search.listing_type==="rent"?"cho-thue-smart-city":"mua-ban-smart-city";
    const params=new URLSearchParams();
    if(search.keyword)params.set("keyword",search.keyword);
    if(search.phase)params.set("phase",search.phase);
    if(search.tower)params.set("tower",search.tower);
    if(search.unit_type)params.set("bedroom",search.unit_type);
    if(search.min_price_vnd)params.set("min_price",String(search.min_price_vnd));
    if(search.max_price_vnd)params.set("max_price",String(search.max_price_vnd));
    const area=areaKey(search);if(area)params.set("area",area);
    if(search.furnishing)params.set("furnishing",search.furnishing);
    return `/${segment}/${params.size?`?${params.toString()}`:""}#quy-can`;
  };

  const savePending=criteria=>{try{localStorage.setItem(pendingKey,JSON.stringify(criteria));}catch{}};
  const readPending=()=>{try{return JSON.parse(localStorage.getItem(pendingKey)||"null");}catch{return null;}};
  const clearPending=()=>{try{localStorage.removeItem(pendingKey);}catch{}};

  window.SmartCitySavedSearches={
    SavedSearchError,normalize,labelFor,fingerprintFor,list,save,remove,touch,countMatches,urlFor,
    savePending,readPending,clearPending,pendingKey
  };
})();
