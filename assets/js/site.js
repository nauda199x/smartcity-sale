(()=>{
  const button=document.querySelector('[data-nav-toggle]');
  const nav=document.querySelector('[data-nav-links]');
  if(button&&nav){
    const dropdowns=[...nav.querySelectorAll('.nav-dropdown')];
    dropdowns.forEach(dropdown=>dropdown.addEventListener('toggle',()=>{
      if(dropdown.open)dropdowns.filter(item=>item!==dropdown).forEach(item=>{item.open=false;});
    }));
    document.addEventListener('click',event=>{
      if(!nav.contains(event.target))dropdowns.forEach(item=>{item.open=false;});
    });
    button.addEventListener('click',()=>{
      const open=nav.getAttribute('data-open')==='true';
      nav.setAttribute('data-open',String(!open));
      button.setAttribute('aria-expanded',String(!open));
    });
    nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{
      dropdowns.forEach(item=>{item.open=false;});
      nav.setAttribute('data-open','false');
      button.setAttribute('aria-expanded','false');
    }));
    document.addEventListener('keydown',event=>{
      if(event.key==='Escape'){
        dropdowns.forEach(item=>{item.open=false;});
        nav.setAttribute('data-open','false');
        button.setAttribute('aria-expanded','false');
      }
    });
  }
  document.querySelectorAll('[data-year]').forEach(el=>{el.textContent=new Date().getFullYear();});
  const reveals=[...document.querySelectorAll('[data-reveal]')];
  if(reveals.length&&'IntersectionObserver' in window&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
    document.documentElement.classList.add('reveal-ready');
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
      if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target);}
    }),{rootMargin:'0px 0px -8%'});
    reveals.forEach(element=>observer.observe(element));
  }
})();

/* Floor-plan image viewer: shared across every /mat-bang-smart-city/ page */
(()=>{
  if(!location.pathname.startsWith('/mat-bang-smart-city/')) return;

  const candidates=[...document.querySelectorAll('main img:not(.article-hero-media)')].filter(img=>{
    if(img.closest('.site-header,.site-footer')) return false;
    const alt=(img.getAttribute('alt')||'').toLowerCase();
    return Boolean(
      img.closest('.tower-plan__media,.plan-frame,.figure,.media-gallery,.masterplan-feature,.lum-story__media,.visual-grid,.ppx-gallery') ||
      alt.includes('mặt bằng') || alt.includes('mat bang') || alt.includes('floor plan') || alt.includes('layout')
    );
  });
  if(!candidates.length) return;

  const viewer=document.createElement('div');
  viewer.className='plan-zoom';
  viewer.setAttribute('aria-hidden','true');
  viewer.innerHTML=`
    <div class="plan-zoom__backdrop" data-plan-zoom-close></div>
    <div class="plan-zoom__panel" role="dialog" aria-modal="true" aria-label="Xem mặt bằng phóng to">
      <div class="plan-zoom__toolbar">
        <div class="plan-zoom__hint">Chụm 2 ngón / lăn chuột để phóng · kéo ảnh khi đã zoom</div>
        <div class="plan-zoom__controls">
          <button type="button" class="plan-zoom__btn" data-plan-zoom-out aria-label="Thu nhỏ">−</button>
          <button type="button" class="plan-zoom__btn plan-zoom__reset" data-plan-zoom-reset aria-label="Đặt lại mức zoom">100%</button>
          <button type="button" class="plan-zoom__btn" data-plan-zoom-in aria-label="Phóng to">+</button>
          <button type="button" class="plan-zoom__btn plan-zoom__close" data-plan-zoom-close aria-label="Đóng">×</button>
        </div>
      </div>
      <div class="plan-zoom__stage" data-plan-zoom-stage>
        <img class="plan-zoom__image" alt="">
      </div>
      <div class="plan-zoom__caption" data-plan-zoom-caption></div>
    </div>`;
  document.body.appendChild(viewer);

  const stage=viewer.querySelector('[data-plan-zoom-stage]');
  const image=viewer.querySelector('.plan-zoom__image');
  const resetBtn=viewer.querySelector('[data-plan-zoom-reset]');
  const caption=viewer.querySelector('[data-plan-zoom-caption]');
  const closeButtons=[...viewer.querySelectorAll('[data-plan-zoom-close]')];
  const inBtn=viewer.querySelector('[data-plan-zoom-in]');
  const outBtn=viewer.querySelector('[data-plan-zoom-out]');

  stage.style.overscrollBehavior='none';
  stage.style.webkitTouchCallout='none';

  const coarsePointer=matchMedia('(pointer: coarse)').matches || navigator.maxTouchPoints>0;
  let touchHint=null;
  if(coarsePointer){
    touchHint=document.createElement('div');
    touchHint.textContent='Chụm 2 ngón để zoom · kéo 1 ngón · chạm đúp để phóng';
    Object.assign(touchHint.style,{
      position:'absolute',
      left:'50%',
      bottom:'12px',
      zIndex:'3',
      transform:'translateX(-50%)',
      width:'max-content',
      maxWidth:'calc(100% - 24px)',
      padding:'8px 11px',
      border:'1px solid rgba(255,255,255,.2)',
      borderRadius:'999px',
      background:'rgba(15,18,16,.78)',
      color:'#f4f1ea',
      font:'600 12px/1.25 system-ui,-apple-system,sans-serif',
      textAlign:'center',
      pointerEvents:'none',
      transition:'opacity .18s ease'
    });
    stage.appendChild(touchHint);
  }

  let scale=1;
  let x=0;
  let y=0;
  let activeThumb=null;
  let pan=null;
  let pinch=null;
  let tapCandidate=null;
  let lastTap=null;
  let suppressDblClickUntil=0;
  const pointers=new Map();

  const minScale=1;
  const maxScale=6;
  const clamp=(value,min,max)=>Math.max(min,Math.min(max,value));

  const constrainPan=()=>{
    if(scale<=1.001){
      x=0;y=0;
      return;
    }
    const baseWidth=image.offsetWidth||0;
    const baseHeight=image.offsetHeight||0;
    const maxX=Math.max(0,(baseWidth*scale-stage.clientWidth)/2+24);
    const maxY=Math.max(0,(baseHeight*scale-stage.clientHeight)/2+24);
    x=clamp(x,-maxX,maxX);
    y=clamp(y,-maxY,maxY);
  };

  const apply=()=>{
    image.style.transform=`translate3d(${x}px,${y}px,0) scale(${scale})`;
    resetBtn.textContent=`${Math.round(scale*100)}%`;
    image.classList.toggle('is-zoomed',scale>1.02);
    if(touchHint) touchHint.style.opacity=scale>1.02?'0':'1';
  };

  const reset=()=>{
    scale=1;x=0;y=0;apply();
  };

  const setScale=(next,clientX=null,clientY=null)=>{
    const previous=scale;
    const nextScale=clamp(next,minScale,maxScale);
    if(Number.isFinite(clientX)&&Number.isFinite(clientY)&&previous>0){
      const rect=stage.getBoundingClientRect();
      const focalX=clientX-(rect.left+rect.width/2);
      const focalY=clientY-(rect.top+rect.height/2);
      const ratio=nextScale/previous;
      x=focalX+(x-focalX)*ratio;
      y=focalY+(y-focalY)*ratio;
    }
    scale=nextScale;
    constrainPan();
    apply();
  };

  const open=(thumb)=>{
    activeThumb=thumb;
    const src=thumb.currentSrc||thumb.src;
    image.src=src;
    image.alt=thumb.alt||'Mặt bằng căn hộ';
    caption.textContent=thumb.alt||'Mặt bằng';
    pointers.clear();
    pan=null;pinch=null;tapCandidate=null;lastTap=null;
    reset();
    viewer.classList.add('is-open');
    viewer.setAttribute('aria-hidden','false');
    document.documentElement.classList.add('plan-zoom-open');
    setTimeout(()=>viewer.querySelector('.plan-zoom__close')?.focus(),0);
  };

  const close=()=>{
    viewer.classList.remove('is-open');
    viewer.setAttribute('aria-hidden','true');
    document.documentElement.classList.remove('plan-zoom-open');
    pointers.clear();
    pan=null;pinch=null;tapCandidate=null;lastTap=null;
    stage.classList.remove('is-dragging');
    image.style.transition='';
    image.removeAttribute('src');
    if(activeThumb) activeThumb.focus({preventScroll:true});
  };

  candidates.forEach(img=>{
    img.classList.add('plan-zoomable');
    img.tabIndex=0;
    if(!img.title) img.title='Bấm để phóng to mặt bằng';
    img.setAttribute('role','button');
    img.setAttribute('aria-label',(img.alt||'Mặt bằng')+' — bấm để phóng to');
    const activate=(event)=>{
      event.preventDefault();
      event.stopPropagation();
      open(img);
    };
    img.addEventListener('click',activate);
    img.addEventListener('keydown',event=>{
      if(event.key==='Enter'||event.key===' '){activate(event);}
    });
  });

  inBtn.addEventListener('click',()=>setScale(scale+0.4));
  outBtn.addEventListener('click',()=>setScale(scale-0.4));
  resetBtn.addEventListener('click',reset);
  closeButtons.forEach(btn=>btn.addEventListener('click',close));

  stage.addEventListener('wheel',event=>{
    event.preventDefault();
    setScale(scale+(event.deltaY<0?0.25:-0.25),event.clientX,event.clientY);
  },{passive:false});

  image.addEventListener('dblclick',event=>{
    if(performance.now()<suppressDblClickUntil) return;
    event.preventDefault();
    setScale(scale>1.35?1:2.5,event.clientX,event.clientY);
  });

  const pointDistance=(a,b)=>Math.hypot(b.x-a.x,b.y-a.y);
  const pointMid=(a,b)=>({x:(a.x+b.x)/2,y:(a.y+b.y)/2});

  const beginPinch=()=>{
    if(pointers.size<2) return;
    const [a,b]=[...pointers.values()].slice(0,2);
    const mid=pointMid(a,b);
    const rect=stage.getBoundingClientRect();
    pinch={
      startDistance:Math.max(1,pointDistance(a,b)),
      startScale:scale,
      startX:x,
      startY:y,
      startMidRelX:mid.x-(rect.left+rect.width/2),
      startMidRelY:mid.y-(rect.top+rect.height/2)
    };
    pan=null;
    stage.classList.remove('is-dragging');
    image.style.transition='none';
  };

  stage.addEventListener('pointerdown',event=>{
    if(event.pointerType==='touch'){
      stage.setPointerCapture?.(event.pointerId);
      pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});
      if(pointers.size===1){
        tapCandidate={id:event.pointerId,x:event.clientX,y:event.clientY,time:performance.now(),moved:false};
        if(scale>1.02){
          pan={id:event.pointerId,startX:event.clientX,startY:event.clientY,originX:x,originY:y};
          stage.classList.add('is-dragging');
          image.style.transition='none';
        }
      }else if(pointers.size===2){
        tapCandidate=null;
        beginPinch();
      }
      return;
    }

    if(scale<=1.02) return;
    stage.setPointerCapture?.(event.pointerId);
    pan={id:event.pointerId,startX:event.clientX,startY:event.clientY,originX:x,originY:y};
    stage.classList.add('is-dragging');
    image.style.transition='none';
  });

  stage.addEventListener('pointermove',event=>{
    if(event.pointerType==='touch'&&pointers.has(event.pointerId)){
      pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});
      if(tapCandidate?.id===event.pointerId&&Math.hypot(event.clientX-tapCandidate.x,event.clientY-tapCandidate.y)>10){
        tapCandidate.moved=true;
      }

      if(pointers.size>=2){
        if(!pinch) beginPinch();
        const [a,b]=[...pointers.values()].slice(0,2);
        const distance=Math.max(1,pointDistance(a,b));
        const mid=pointMid(a,b);
        const rect=stage.getBoundingClientRect();
        const currentMidRelX=mid.x-(rect.left+rect.width/2);
        const currentMidRelY=mid.y-(rect.top+rect.height/2);
        const nextScale=clamp(pinch.startScale*(distance/pinch.startDistance),minScale,maxScale);
        const ratio=nextScale/pinch.startScale;
        scale=nextScale;
        x=currentMidRelX-(pinch.startMidRelX-pinch.startX)*ratio;
        y=currentMidRelY-(pinch.startMidRelY-pinch.startY)*ratio;
        constrainPan();
        apply();
        return;
      }
    }

    if(!pan||pan.id!==event.pointerId) return;
    x=pan.originX+(event.clientX-pan.startX);
    y=pan.originY+(event.clientY-pan.startY);
    constrainPan();
    apply();
  });

  const finishPointer=(event,cancelled=false)=>{
    const wasTouch=event.pointerType==='touch';
    const wasSingleTouch=wasTouch&&pointers.size===1&&pointers.has(event.pointerId);
    const tap=tapCandidate?.id===event.pointerId?tapCandidate:null;
    const hadPinch=Boolean(pinch);

    if(wasTouch) pointers.delete(event.pointerId);
    try{stage.releasePointerCapture?.(event.pointerId);}catch(_){}

    if(wasTouch&&wasSingleTouch&&!cancelled&&!hadPinch&&tap&&!tap.moved&&performance.now()-tap.time<320){
      const now=performance.now();
      if(lastTap&&now-lastTap.time<330&&Math.hypot(event.clientX-lastTap.x,event.clientY-lastTap.y)<42){
        suppressDblClickUntil=now+550;
        setScale(scale>1.35?1:2.5,event.clientX,event.clientY);
        lastTap=null;
      }else{
        lastTap={time:now,x:event.clientX,y:event.clientY};
      }
    }

    tapCandidate=null;
    if(wasTouch&&pointers.size>=2){
      beginPinch();
      return;
    }

    pinch=null;
    if(wasTouch&&pointers.size===1&&scale>1.02){
      const [id,point]=[...pointers.entries()][0];
      pan={id,startX:point.x,startY:point.y,originX:x,originY:y};
      stage.classList.add('is-dragging');
      image.style.transition='none';
      return;
    }

    pan=null;
    stage.classList.remove('is-dragging');
    image.style.transition='';
  };

  stage.addEventListener('pointerup',event=>finishPointer(event,false));
  stage.addEventListener('pointercancel',event=>finishPointer(event,true));

  window.addEventListener('resize',()=>{
    constrainPan();
    apply();
  },{passive:true});

  document.addEventListener('keydown',event=>{
    if(!viewer.classList.contains('is-open')) return;
    if(event.key==='Escape') close();
    if(event.key==='+'||event.key==='=') setScale(scale+0.4);
    if(event.key==='-') setScale(scale-0.4);
    if(event.key==='0') reset();
  });
})();
