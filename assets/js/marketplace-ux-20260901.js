(()=>{
  const form=document.querySelector("[data-post-wizard]");
  if(!form)return;

  const sections=[...form.querySelectorAll("[data-form-step]")];
  const progressButtons=[...form.querySelectorAll("[data-progress-step]")];
  const progressCurrent=form.querySelector("[data-progress-current]");
  const progressBar=form.querySelector("[data-progress-bar]");
  const status=form.querySelector("[data-form-status]");
  const filesInput=form.querySelector('[name="images"]');
  const previews=form.querySelector("[data-image-previews]");
  const imageCount=form.querySelector("[data-image-count]");
  const description=form.querySelector('[name="description"]');
  const descriptionCount=form.querySelector("[data-description-count]");
  const titleInput=form.querySelector('[name="title"]');
  const generateTitleButton=form.querySelector("[data-generate-title]");
  const mobileBar=form.querySelector("[data-mobile-wizard-bar]");
  const mobileBack=form.querySelector("[data-mobile-wizard-back]");
  const mobileNext=form.querySelector("[data-mobile-wizard-next]");
  const mobileSubmit=form.querySelector("[data-mobile-wizard-submit]");
  const mobileStepLabel=form.querySelector("[data-mobile-step-label]");
  const mobileStepName=form.querySelector("[data-mobile-step-name]");
  const mq=matchMedia("(max-width:760px)");
  const stepNames=["Loại tin","Căn hộ","Ảnh & mô tả","Liên hệ"];
  const phaseSelect=form.querySelector('[name="phase"]');
  const unitTypeSelect=form.querySelector('[name="unit_type"]');
  const unitTypeHelp=form.querySelector("[data-unit-type-help]");
  const phaseUnitTypes={
    "Sapphire":["Studio","1PN","1PN+1","2PN","2PN+1 (1WC)","2PN+1 (2WC)","3PN","Shop chân đế"],
    "Sakura":["Studio","1PN","1PN+1","2PN","2PN+1","3PN","Shop chân đế"],
    "Miami":["Studio","1PN","1PN+1","2PN","2PN+1","3PN","Shop chân đế"],
    "Tonkin":["Studio","1PN","1PN+1","2PN","2PN+1","3PN","Shop chân đế"],
    "Masteri":["Studio","1PN+1","2PN","2PN+1","3PN","Shop chân đế"],
    "Lumiere":["Studio","1PN","1PN+","2PN","2PN+","3PN","4PN","Shop chân đế"],
    "Imperia":["Studio","1PN+1","2PN","2PN+1","3PN","Shop chân đế"],
    "Canopy":["Studio","1PN","2PN","2PN+1","3PN","3PN+1","Shop chân đế"],
    "Sola Park":["Studio","1PN+1","2PN","2PN+1","3PN","Shop chân đế"],
    "Victoria":["Studio","1PN","1PN+","2PN","2PN+","3PN","Shop chân đế"]
  };
  let currentStep=1;

  const q=name=>form.elements[name];
  const equivalentUnitTypes=value=>{
    const v=String(value||"");
    if(v==="1PN+")return ["1PN+","1PN+1"];
    if(v==="1PN+1")return ["1PN+1","1PN+"];
    if(v==="2PN+")return ["2PN+","2PN+1","2PN+1 (1WC)","2PN+1 (2WC)"];
    if(v==="2PN+1")return ["2PN+1","2PN+","2PN+1 (1WC)","2PN+1 (2WC)"];
    if(v.startsWith("2PN+1 ("))return [v,"2PN+1","2PN+"];
    if(v==="3PN+")return ["3PN+","3PN+1"];
    if(v==="3PN+1")return ["3PN+1","3PN+"];
    return [v];
  };
  const refreshUnitTypes=()=>{
    if(!unitTypeSelect)return;
    const phase=phaseSelect?.value||"";
    const current=unitTypeSelect.value;
    const options=phaseUnitTypes[phase]||[...new Set(Object.values(phaseUnitTypes).flat())];
    unitTypeSelect.replaceChildren(
      new Option(phase?"Chọn loại căn":"Chọn phân khu trước",""),
      ...options.map(value=>new Option(value,value))
    );
    const restored=equivalentUnitTypes(current).find(value=>options.includes(value));
    if(restored)unitTypeSelect.value=restored;
    unitTypeSelect.disabled=!phase;
    if(unitTypeHelp){
      unitTypeHelp.textContent=phase
        ?`Loại căn theo đúng cơ cấu ${phase} tại Smart City.`
        :"Chọn phân khu trước, hệ thống sẽ hiện đúng loại căn của khu đó.";
    }
  };
  const checkedType=()=>form.querySelector('[name="listing_type"]:checked')?.value||"sale";
  const clean=value=>String(value||"").trim();
  const fieldLabel=element=>{
    if(!element?.id)return "thông tin bắt buộc";
    const label=form.querySelector(`label[for="${CSS.escape(element.id)}"]`);
    return label?.textContent?.replace(/\s*\*\s*$/,"").trim()||"thông tin bắt buộc";
  };

  const ensureStepError=section=>{
    let box=section.querySelector(".post-step-error");
    if(!box){
      box=document.createElement("p");
      box.className="post-step-error";
      box.setAttribute("role","alert");
      box.hidden=true;
      section.querySelector(".form-section-head")?.insertAdjacentElement("afterend",box);
    }
    return box;
  };
  const clearStepError=section=>{
    const box=section?.querySelector(".post-step-error");
    if(box){box.hidden=true;box.textContent="";}
  };
  const showStepError=(section,message)=>{
    const box=ensureStepError(section);
    box.textContent=message;
    box.hidden=false;
  };

  const syncImageValidity=()=>{
    if(!filesInput)return true;
    const count=filesInput.files?.length||0;
    filesInput.setCustomValidity(count?"":"Vui lòng chọn ít nhất 1 ảnh căn hộ.");
    if(imageCount){
      imageCount.textContent=count
        ?`${count} ảnh đã chọn · ảnh đầu tiên là ảnh đại diện`
        :"Chưa chọn ảnh · ảnh đầu tiên sẽ là ảnh đại diện";
      imageCount.classList.toggle("has-images",count>0);
    }
    return count>0;
  };

  const requiredInSection=section=>[...section.querySelectorAll("input,select,textarea")].filter(el=>
    !el.disabled&&el.name!=="website"&&el.type!=="hidden"&&el.type!=="file"&&el.required
  );

  const validateSection=step=>{
    const section=sections[step-1];
    if(!section)return true;
    clearStepError(section);
    if(step===3&&!syncImageValidity()){
      showStepError(section,"Anh/chị chọn ít nhất 1 ảnh căn hộ trước khi tiếp tục.");
      filesInput?.closest(".post-image-drop")?.scrollIntoView({behavior:"smooth",block:"center"});
      return false;
    }

    const required=requiredInSection(section);
    for(const el of required){
      if(el.type==="radio"){
        const group=[...section.querySelectorAll(`input[type="radio"][name="${CSS.escape(el.name)}"]`)];
        if(group.some(item=>item.checked))continue;
      }
      if(!el.checkValidity()){
        el.setAttribute("aria-invalid","true");
        const message=el.validity.valueMissing
          ?`Vui lòng điền “${fieldLabel(el)}”.`
          :`Vui lòng kiểm tra lại “${fieldLabel(el)}”.`;
        showStepError(section,message);
        try{el.focus({preventScroll:true});}catch(_){}
        el.scrollIntoView({behavior:"smooth",block:"center"});
        return false;
      }
    }
    return true;
  };

  const setProgressVisual=step=>{
    if(progressCurrent)progressCurrent.textContent=`Bước ${step}/4`;
    if(progressBar)progressBar.style.width=`${step*25}%`;
    progressButtons.forEach((button,index)=>{
      const n=index+1;
      button.classList.toggle("is-active",n===step);
      button.classList.toggle("is-complete",n<step);
      if(n===step)button.setAttribute("aria-current","step");
      else button.removeAttribute("aria-current");
    });
  };

  const showStep=(step,{scroll=true}={})=>{
    currentStep=Math.max(1,Math.min(4,Number(step)||1));
    setProgressVisual(currentStep);
    if(mq.matches){
      form.classList.add("is-mobile-wizard");
      sections.forEach((section,index)=>section.classList.toggle("is-wizard-active",index+1===currentStep));
      if(mobileStepLabel)mobileStepLabel.textContent=`Bước ${currentStep}/4`;
      if(mobileStepName)mobileStepName.textContent=stepNames[currentStep-1];
      if(mobileBack)mobileBack.disabled=currentStep===1;
      if(mobileNext)mobileNext.hidden=currentStep===4;
      if(mobileSubmit)mobileSubmit.hidden=currentStep!==4;
      if(scroll){
        const progress=form.querySelector("[data-form-progress]");
        const top=(progress?.getBoundingClientRect().top||0)+window.scrollY-74;
        window.scrollTo({top:Math.max(0,top),behavior:"smooth"});
      }
    }else{
      form.classList.remove("is-mobile-wizard");
      sections.forEach(section=>section.classList.remove("is-wizard-active"));
    }
  };

  const next=()=>{
    if(currentStep>=4)return;
    if(!validateSection(currentStep))return;
    showStep(currentStep+1);
  };
  const back=()=>{
    if(currentStep>1)showStep(currentStep-1);
  };

  form.querySelectorAll("[data-wizard-next]").forEach(btn=>btn.addEventListener("click",()=>{
    const section=btn.closest("[data-form-step]");
    if(section)currentStep=Number(section.dataset.formStep)||currentStep;
    next();
  }));
  form.querySelectorAll("[data-wizard-back]").forEach(btn=>btn.addEventListener("click",()=>{
    const section=btn.closest("[data-form-step]");
    if(section)currentStep=Number(section.dataset.formStep)||currentStep;
    back();
  }));
  mobileNext?.addEventListener("click",next);
  mobileBack?.addEventListener("click",back);

  progressButtons.forEach((button,index)=>{
    button.addEventListener("click",event=>{
      if(!mq.matches)return;
      event.preventDefault();
      event.stopImmediatePropagation();
      const target=index+1;
      if(target===currentStep)return;
      if(target<currentStep){showStep(target);return;}
      if(target===currentStep+1&&validateSection(currentStep))showStep(target);
    },true);
  });

  const generatedTitle=()=>{
    const type=checkedType()==="rent"?"Cho thuê":"Bán";
    const unit=clean(q("unit_type")?.value);
    const phase=clean(q("phase")?.value);
    const tower=clean(q("tower")?.value);
    const floor=clean(q("floor_label")?.value);
    const furnishing=clean(q("furnishing")?.value);
    const location=[phase,tower].filter(Boolean).join(" ");
    const parts=[type,unit||"căn hộ",location].filter(Boolean);
    if(floor)parts.push(`tầng ${floor.toLowerCase()}`);
    if(furnishing)parts.push(furnishing.toLowerCase());
    return parts.join(", ").replace(/^([^,]+),/,"$1").replace(/, ([^,]+)$/,", $1");
  };

  generateTitleButton?.addEventListener("click",()=>{
    if(!titleInput)return;
    titleInput.value=generatedTitle();
    titleInput.dispatchEvent(new Event("input",{bubbles:true}));
    titleInput.focus();
  });

  form.querySelectorAll("[data-description-prompt]").forEach(button=>{
    button.addEventListener("click",()=>{
      if(!description)return;
      const text=button.dataset.descriptionPrompt||"";
      const before=description.value.trim();
      description.value=before?`${before}\n${text}`:text;
      description.dispatchEvent(new Event("input",{bubbles:true}));
      description.focus();
      description.setSelectionRange(description.value.length,description.value.length);
    });
  });

  const previewType=document.querySelector("[data-post-preview-type]");
  const previewTitle=document.querySelector("[data-post-preview-title]");
  const previewLocation=document.querySelector("[data-post-preview-location]");
  const previewUnit=document.querySelector("[data-post-preview-unit]");
  const previewArea=document.querySelector("[data-post-preview-area]");
  const previewPrice=document.querySelector("[data-post-preview-price]");
  const previewImages=document.querySelector("[data-post-preview-images]");
  const completion=document.querySelector("[data-post-completion]");
  const completionBar=document.querySelector("[data-post-completion-bar]");

  const priceText=()=>{
    const value=clean(q("price_vnd")?.value);
    if(!value)return "—";
    return checkedType()==="rent"
      ?(value.toLowerCase().includes("triệu")?value:`${value} triệu/tháng`)
      :(value.toLowerCase().includes("tỷ")?value:`${value} tỷ`);
  };
  const updatePreview=()=>{
    const phase=clean(q("phase")?.value);
    const tower=clean(q("tower")?.value);
    const unit=clean(q("unit_type")?.value);
    const area=clean(q("area_sqm")?.value);
    const count=filesInput?.files?.length||0;
    if(previewType)previewType.textContent=checkedType()==="rent"?"Đang đăng căn cho thuê":"Đang đăng căn bán";
    if(previewTitle)previewTitle.textContent=clean(titleInput?.value)||generatedTitle()||"Tiêu đề tin sẽ hiện ở đây";
    if(previewLocation)previewLocation.textContent=[phase,tower].filter(Boolean).join(" / ")||"Chưa chọn phân khu / tòa";
    if(previewUnit)previewUnit.textContent=unit||"Chưa chọn";
    if(previewArea)previewArea.textContent=area?`${area} m²`:"—";
    if(previewPrice)previewPrice.textContent=priceText();
    if(previewImages)previewImages.textContent=`${count} ảnh`;
    if(descriptionCount)descriptionCount.textContent=`${description?.value.length||0}/3000`;

    const checks=[
      Boolean(form.querySelector('[name="listing_type"]:checked')),
      Boolean(phase),Boolean(tower),Boolean(unit),Boolean(area),Boolean(clean(q("price_vnd")?.value)),
      Boolean(clean(titleInput?.value)),Boolean(clean(description?.value)&&description.value.trim().length>=30),
      count>0,Boolean(clean(q("poster_name")?.value)),Boolean(clean(q("contact_phone")?.value)),
      Boolean(q("contact_public")?.checked)
    ];
    const pct=Math.round(checks.filter(Boolean).length/checks.length*100);
    if(completion)completion.textContent=`${pct}%`;
    if(completionBar)completionBar.style.width=`${pct}%`;
  };

  const decoratePreviews=()=>{
    const figures=[...(previews?.querySelectorAll(".image-preview")||[])];
    figures.forEach((figure,index)=>{
      if(figure.querySelector(".post-image-remove"))return;
      if(typeof DataTransfer==="undefined")return;
      const button=document.createElement("button");
      button.type="button";
      button.className="post-image-remove";
      button.setAttribute("aria-label",`Xóa ảnh ${index+1}`);
      button.textContent="×";
      button.addEventListener("click",()=>{
        const files=[...(filesInput?.files||[])];
        const dt=new DataTransfer();
        files.forEach((file,fileIndex)=>{if(fileIndex!==index)dt.items.add(file);});
        filesInput.files=dt.files;
        filesInput.dispatchEvent(new Event("change",{bubbles:true}));
      });
      figure.append(button);
    });
  };

  if(previews){
    new MutationObserver(()=>{
      decoratePreviews();
      updatePreview();
    }).observe(previews,{childList:true});
  }

  filesInput?.addEventListener("change",()=>{
    syncImageValidity();
    requestAnimationFrame(()=>{decoratePreviews();updatePreview();});
  });

  form.addEventListener("input",event=>{
    event.target?.removeAttribute?.("aria-invalid");
    clearStepError(event.target?.closest?.("[data-form-step]"));
    updatePreview();
  });
  form.addEventListener("change",event=>{
    if(event.target===phaseSelect)refreshUnitTypes();
    event.target?.removeAttribute?.("aria-invalid");
    clearStepError(event.target?.closest?.("[data-form-step]"));
    requestAnimationFrame(updatePreview);
  });

  form.addEventListener("submit",event=>{
    syncImageValidity();
    for(let step=1;step<=4;step++){
      if(!validateSection(step)){
        event.preventDefault();
        event.stopImmediatePropagation();
        if(mq.matches)showStep(step,{scroll:false});
        return;
      }
    }
  },true);

  form.addEventListener("reset",()=>{
    setTimeout(()=>{
      currentStep=1;
      showStep(1,{scroll:false});
      syncImageValidity();
      updatePreview();
    },0);
  });

  const applyMode=()=>{
    if(mq.matches)showStep(currentStep,{scroll:false});
    else showStep(currentStep,{scroll:false});
  };
  mq.addEventListener?.("change",applyMode);

  if(window.visualViewport){
    const keyboardState=()=>{
      if(!mq.matches)return;
      const open=window.visualViewport.height<window.innerHeight*.72;
      form.classList.toggle("is-keyboard-open",open);
    };
    window.visualViewport.addEventListener("resize",keyboardState);
    keyboardState();
  }

  refreshUnitTypes();
  syncImageValidity();
  updatePreview();
  decoratePreviews();
  showStep(1,{scroll:false});
})();