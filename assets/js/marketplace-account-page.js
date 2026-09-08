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
  const counts={
    all:document.querySelector("[data-count-all]"),
    approved:document.querySelector("[data-count-approved]"),
    pending:document.querySelector("[data-count-pending]"),
    stale:document.querySelector("[data-count-stale]"),
    hidden:document.querySelector("[data-count-hidden]")
  };
  const statusLabels={pending:"Chờ duyệt",approved:"Đang hiển thị",rejected:"Bị từ chối",expired:"Đã ẩn / hết hạn",sold:"Đã bán",rented:"Đã cho thuê"};

  const bulkFile=document.querySelector("[data-bulk-file]");
  const bulkImport=document.querySelector("[data-bulk-import]");
  const bulkSummary=document.querySelector("[data-bulk-summary]");
  const bulkPreview=document.querySelector("[data-bulk-preview]");
  let parsedBulk=[];
  let bulkIssues=[];

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

  const daysSince=value=>{
    const date=new Date(value||"");
    if(Number.isNaN(date.getTime()))return 9999;
    return Math.max(0,Math.floor((Date.now()-date.getTime())/86400000));
  };

  const freshnessFor=listing=>{
    const days=daysSince(listing.last_confirmed_at||listing.created_at);
    if(days===0)return {days,level:"fresh",label:"Còn hàng · xác nhận hôm nay"};
    if(days<=7)return {days,level:"fresh",label:`Còn hàng · xác nhận ${days} ngày trước`};
    if(days<=21)return {days,level:"ok",label:`Đã xác nhận ${days} ngày trước`};
    return {days,level:"stale",label:`Cần xác nhận lại · ${days} ngày`};
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
        :action==="hide"?"Ẩn tin này khỏi sàn?"
        :action==="confirm"?"Xác nhận căn này hiện vẫn còn hàng? Mốc xác nhận sẽ được làm mới."
        :"Gửi tin này về trạng thái chờ duyệt lại?";
      if(!confirm(confirmText))return;
      buttonBusy(button,true,"Đang xử lý…");
      try{
        await account.ownerAction(listing.id,action);
        setStatus(action==="confirm"?"Đã xác nhận căn vẫn còn hàng.":"Đã cập nhật trạng thái tin.","success");
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
    const code=document.createElement("div");
    code.className="member-listing__code";
    code.textContent=`${listing.listing_code||"Tin đăng"}${listing.source_channel==="bulk"?" · CSV":""}`;
    const title=document.createElement("h3");title.textContent=listing.title||"Tin chưa có tiêu đề";
    const meta=document.createElement("div");meta.className="member-listing__meta";
    [
      listing.phase&&`${listing.phase}${listing.tower?` · ${listing.tower}`:""}`,
      listing.unit_type,
      listing.price_vnd&&api.formatCurrency(listing.price_vnd,listing.listing_type),
      Number(listing.view_count||0)>0&&`${Number(listing.view_count).toLocaleString("vi-VN")} lượt xem`,
      listing.created_at&&`Đăng ${formatDate(listing.created_at)}`
    ].filter(Boolean).forEach(text=>{const span=document.createElement("span");span.textContent=text;meta.append(span);});
    const badges=document.createElement("div");badges.className="member-listing__badges";
    const badge=document.createElement("span");badge.className="member-badge";badge.dataset.status=listing.status||"";badge.textContent=statusLabels[listing.status]||listing.status||"Không rõ";
    badges.append(badge);
    if(["approved","pending"].includes(listing.status)){
      const fresh=freshnessFor(listing);
      const freshness=document.createElement("span");freshness.className="member-freshness";freshness.dataset.level=fresh.level;freshness.textContent=fresh.label;badges.append(freshness);
    }
    body.append(code,title,meta,badges);

    const actions=document.createElement("div");actions.className="member-listing__actions";
    if(listing.status==="approved"&&listing.slug){
      const link=document.createElement("a");link.href=api.listingUrl(listing);link.textContent="Xem tin";link.className="is-primary";actions.append(link);
    }
    if(["approved","pending"].includes(listing.status))actions.append(actionButton(listing,"confirm","✓ Còn hàng","is-confirm"));
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
    const stale=rows.filter(row=>["approved","pending"].includes(row.status)&&freshnessFor(row).days>21).length;
    const hidden=rows.filter(row=>["expired","rejected","sold","rented"].includes(row.status)).length;
    if(counts.all)counts.all.textContent=rows.length;
    if(counts.approved)counts.approved.textContent=active;
    if(counts.pending)counts.pending.textContent=pending;
    if(counts.stale)counts.stale.textContent=stale;
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
      updateCounts(rows);renderListings(rows);
    }catch(error){
      renderListings([]);setStatus(error.message||"Chưa tải được danh sách tin.","error");
    }
  }

  const fold=value=>String(value??"").trim().normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/đ/g,"d").replace(/[^a-z0-9+]+/g," ").trim().replace(/\s+/g," ");
  const compact=value=>fold(value).replace(/\s+/g,"");
  const clean=value=>String(value??"").trim();

  const parseCsv=text=>{
    const rows=[];let row=[];let field="";let quoted=false;
    const source=String(text||"").replace(/^\uFEFF/,"");
    for(let i=0;i<source.length;i++){
      const char=source[i];
      if(quoted){
        if(char==='"'&&source[i+1]==='"'){field+='"';i++;}
        else if(char==='"')quoted=false;
        else field+=char;
      }else if(char==='"')quoted=true;
      else if(char===','){row.push(field);field="";}
      else if(char==='\n'){row.push(field);rows.push(row);row=[];field="";}
      else if(char!=='\r')field+=char;
    }
    row.push(field);if(row.some(value=>String(value).trim()))rows.push(row);
    return rows;
  };

  const headerKey=value=>fold(value).replace(/\s+/g,"_");
  const pick=(record,...keys)=>{
    for(const key of keys){if(record[key]!==undefined&&clean(record[key])!=="")return clean(record[key]);}
    return "";
  };
  const parseFlexibleNumber=value=>{
    let raw=clean(value).replace(/\s+/g,"").replace(/[^\d.,-]/g,"");
    if(!raw)return NaN;
    if(raw.includes(",")&&!raw.includes("."))raw=raw.replace(",",".");
    else if(raw.includes(",")&&raw.includes("."))raw=raw.replace(/,/g,"");
    return Number(raw);
  };

  const typeFrom=value=>{
    const key=compact(value);
    if(["ban","sale","muaban"].includes(key))return "sale";
    if(["thue","rent","chothue"].includes(key))return "rent";
    return "";
  };
  const phaseFrom=value=>{
    const key=fold(value);
    const aliases={
      "sapphire":"Sapphire","the sapphire":"Sapphire",
      "sakura":"Sakura","the sakura":"Sakura",
      "miami":"Miami","the miami":"Miami",
      "tonkin":"Tonkin","the tonkin":"Tonkin",
      "masteri":"Masteri","masteri west heights":"Masteri",
      "lumiere":"Lumiere","lumiere evergreen":"Lumiere",
      "imperia":"Imperia","imperia smart city":"Imperia",
      "canopy":"Canopy","the canopy":"Canopy","the canopy residences":"Canopy",
      "sola park":"Sola Park","the sola park":"Sola Park",
      "victoria":"Victoria","the victoria":"Victoria"
    };
    return aliases[key]||"";
  };
  const unitTypeFrom=value=>{
    const key=compact(value);
    const aliases={
      "studio":"Studio","1pn":"1PN","1n":"1PN",
      "1pn+":"1PN+1","1n+":"1PN+1","1pn+1":"1PN+1","1n+1":"1PN+1",
      "2pn":"2PN","2n":"2PN","2pn+":"2PN+1","2n+":"2PN+1","2pn+1":"2PN+1","2n+1":"2PN+1",
      "3pn":"3PN","3n":"3PN","3pn+1":"3PN+1","3n+1":"3PN+1",
      "4pn":"4PN","4n":"4PN","shop":"Shop chân đế","shopchande":"Shop chân đế"
    };
    return aliases[key]||"";
  };
  const floorFrom=value=>{
    const key=fold(value);
    if(!key)return null;
    if(["thap","low"].includes(key))return "Thấp";
    if(["trung","middle","mid"].includes(key))return "Trung";
    if(["cao","high"].includes(key))return "Cao";
    return "";
  };
  const bedroomFrom=unitType=>{
    if(/^1PN/.test(unitType))return 1;if(/^2PN/.test(unitType))return 2;if(/^3PN/.test(unitType))return 3;if(/^4PN/.test(unitType))return 4;return null;
  };
  const posterTypeFrom=value=>["chu nha","owner"].includes(fold(value))?"owner":"agent";

  const listingFromCsv=(record,rowNumber)=>{
    const errors=[];
    const listingType=typeFrom(pick(record,"loai_giao_dich","giao_dich","loai"));
    if(!listingType)errors.push("loại giao dịch phải là bán hoặc thuê");
    const phase=phaseFrom(pick(record,"phan_khu","phankhu"));
    if(!phase)errors.push("phân khu chưa đúng tên chuẩn");
    const tower=pick(record,"toa","toa_nha","tower").slice(0,80);
    if(!tower)errors.push("thiếu tòa");
    const unitType=unitTypeFrom(pick(record,"loai_can","loaican","unit_type"));
    if(!unitType)errors.push("loại căn chưa hợp lệ");
    const area=parseFlexibleNumber(pick(record,"dien_tich","dientich","area"));
    if(!Number.isFinite(area)||area<20||area>1000)errors.push("diện tích phải từ 20–1000 m²");
    const rawFloor=pick(record,"tang","nhom_tang","floor");
    const floor=floorFrom(rawFloor);
    if(rawFloor&&floor==="")errors.push("tầng chỉ dùng Thấp / Trung / Cao");
    const rawPrice=parseFlexibleNumber(pick(record,"gia","price"));
    let price=rawPrice;
    if(Number.isFinite(rawPrice)&&rawPrice>0&&rawPrice<1_000_000)price=rawPrice*(listingType==="sale"?1_000_000_000:1_000_000);
    if(!Number.isFinite(price)||price<1_000_000)errors.push("giá chưa hợp lệ");
    const posterName=pick(record,"ten_nguoi_dang","ten","poster_name").slice(0,120);
    if(posterName.length<2)errors.push("thiếu tên người đăng");
    const phone=pick(record,"so_dien_thoai","sdt","phone").slice(0,30);
    if(phone.length<8)errors.push("số điện thoại quá ngắn");
    const unitCode=pick(record,"ma_noi_bo","ma_can","unit_code").slice(0,40)||null;
    const furnishing=pick(record,"noi_that","noithat","furnishing").slice(0,80)||null;
    const zalo=pick(record,"zalo").slice(0,30)||null;
    const role=posterTypeFrom(pick(record,"vai_tro","poster_type"));
    let title=pick(record,"tieu_de","tieude","title").slice(0,180);
    if(title.length<10&&listingType&&unitType&&phase&&tower&&Number.isFinite(area))title=`${listingType==="rent"?"Cho thuê":"Bán"} căn ${unitType} ${phase} ${tower} ${area}m²`;
    let description=pick(record,"mo_ta","mota","description").slice(0,3000);
    if(!description&&listingType&&unitType&&phase&&tower&&Number.isFinite(area))description=`${listingType==="rent"?"Cho thuê":"Bán"} căn ${unitType} tại ${phase} ${tower}, diện tích ${area} m². Liên hệ người đăng để xác nhận tình trạng căn và xem thực tế.`;
    if(title.length<10)errors.push("tiêu đề quá ngắn");
    if(!description)errors.push("thiếu mô tả");

    return {
      rowNumber,errors,
      listing:{
        listing_type:listingType,title,description,phase,tower,unit_type:unitType,
        bedroom_count:bedroomFrom(unitType),area_sqm:Number.isFinite(area)?area:0,
        floor_label:floor||null,unit_code:unitCode,price_vnd:Number.isFinite(price)?Math.round(price):0,
        furnishing,direction:null,view_text:null,available_from:null,legal_status:null,
        poster_type:role,poster_name:posterName,contact_phone:phone,contact_zalo:zalo,contact_email:null,
        contact_public:true
      }
    };
  };

  const renderBulkPreview=items=>{
    if(!bulkPreview)return;
    bulkPreview.replaceChildren();
    if(!items.length){bulkPreview.hidden=true;return;}
    bulkPreview.hidden=false;
    const table=document.createElement("table");table.className="member-bulk-table";
    const head=document.createElement("thead");head.innerHTML="<tr><th>Dòng</th><th>Căn</th><th>Giá</th><th>Kiểm tra</th></tr>";table.append(head);
    const body=document.createElement("tbody");
    items.slice(0,10).forEach(item=>{
      const tr=document.createElement("tr");
      const values=[
        item.rowNumber,
        [item.listing.phase,item.listing.tower,item.listing.unit_type].filter(Boolean).join(" · ")||"—",
        item.listing.price_vnd?api.formatCurrency(item.listing.price_vnd,item.listing.listing_type):"—",
        item.errors.length?`Lỗi: ${item.errors.join("; ")}`:"Sẵn sàng"
      ];
      values.forEach((value,index)=>{const td=document.createElement("td");td.textContent=String(value);if(index===3)td.className=item.errors.length?"is-error":"is-ready";tr.append(td);});
      body.append(tr);
    });
    table.append(body);bulkPreview.append(table);
    if(items.length>10){const more=document.createElement("p");more.className="member-bulk-more";more.textContent=`… và ${items.length-10} dòng khác trong file.`;bulkPreview.append(more);}
  };

  const resetBulk=()=>{
    parsedBulk=[];bulkIssues=[];
    if(bulkFile)bulkFile.value="";
    if(bulkSummary)bulkSummary.textContent="Chưa chọn file CSV.";
    if(bulkImport)bulkImport.disabled=true;
    renderBulkPreview([]);
  };

  bulkFile?.addEventListener("change",async()=>{
    setStatus("");parsedBulk=[];bulkIssues=[];
    const file=bulkFile.files?.[0];
    if(!file){resetBulk();return;}
    if(file.size>1_000_000){setStatus("File CSV quá lớn. Hãy chia quỹ hàng thành các file tối đa 50 căn.","error");resetBulk();return;}
    try{
      const rows=parseCsv(await file.text());
      if(rows.length<2)throw new Error("File chưa có dòng dữ liệu.");
      const headers=rows[0].map(headerKey);
      const items=rows.slice(1).filter(row=>row.some(value=>clean(value))).map((row,index)=>{
        const record={};headers.forEach((key,column)=>{record[key]=row[column]??"";});
        return listingFromCsv(record,index+2);
      });
      if(items.length>50){setStatus(`File có ${items.length} căn. Mỗi lần tối đa 50 căn để dễ kiểm tra và duyệt.`,"error");renderBulkPreview(items);if(bulkImport)bulkImport.disabled=true;return;}
      parsedBulk=items.filter(item=>!item.errors.length);
      bulkIssues=items.filter(item=>item.errors.length);
      if(bulkSummary)bulkSummary.textContent=`${parsedBulk.length} căn hợp lệ${bulkIssues.length?` · ${bulkIssues.length} dòng cần sửa`:""}.`;
      if(bulkImport)bulkImport.disabled=!parsedBulk.length;
      renderBulkPreview(items);
    }catch(error){
      setStatus(error.message||"Không đọc được file CSV.","error");resetBulk();
    }
  });

  bulkImport?.addEventListener("click",async()=>{
    if(!parsedBulk.length)return;
    const count=parsedBulk.length;
    if(!confirm(`Gửi ${count} căn hợp lệ vào hàng chờ duyệt? Hệ thống sẽ tự bỏ qua căn trùng trong tài khoản.`))return;
    buttonBusy(bulkImport,true,"Đang đăng quỹ hàng…");
    try{
      const result=await account.bulkCreateListings(parsedBulk.map(item=>item.listing));
      const created=result.created.length;
      const skipped=result.skipped.length;
      const invalid=bulkIssues.length;
      setStatus(`Đã gửi ${created} căn vào hàng chờ duyệt${skipped?` · bỏ qua ${skipped} căn trùng`:""}${invalid?` · ${invalid} dòng lỗi chưa đăng`:""}.`,"success");
      resetBulk();await loadDashboard();
    }catch(error){setStatus(error.message||"Chưa đăng được quỹ hàng.","error");}
    finally{buttonBusy(bulkImport,false,"");}
  });

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

  resetBulk();
  loadDashboard().catch(()=>showAuth());
})();