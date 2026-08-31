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
        <div class="plan-zoom__hint">Lăn chuột / dùng nút + − để phóng · kéo ảnh khi đã zoom</div>
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

  let scale=1;
  let x=0;
  let y=0;
  let dragging=false;
  let dragStartX=0;
  let dragStartY=0;
  let originX=0;
  let originY=0;
  let activeThumb=null;

  const minScale=0.5;
  const maxScale=5;

  const apply=()=>{
    image.style.transform=`translate3d(${x}px,${y}px,0) scale(${scale})`;
    resetBtn.textContent=`${Math.round(scale*100)}%`;
    image.classList.toggle('is-zoomed',scale>1.02);
  };

  const reset=()=>{
    scale=1;x=0;y=0;apply();
  };

  const setScale=(next)=>{
    scale=Math.max(minScale,Math.min(maxScale,next));
    if(scale<=1){x=0;y=0;}
    apply();
  };

  const open=(thumb)=>{
    activeThumb=thumb;
    const src=thumb.currentSrc||thumb.src;
    image.src=src;
    image.alt=thumb.alt||'Mặt bằng căn hộ';
    caption.textContent=thumb.alt||'Mặt bằng';
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

  inBtn.addEventListener('click',()=>setScale(scale+0.25));
  outBtn.addEventListener('click',()=>setScale(scale-0.25));
  resetBtn.addEventListener('click',reset);
  closeButtons.forEach(btn=>btn.addEventListener('click',close));

  stage.addEventListener('wheel',event=>{
    event.preventDefault();
    setScale(scale+(event.deltaY<0?0.2:-0.2));
  },{passive:false});

  image.addEventListener('dblclick',event=>{
    event.preventDefault();
    setScale(scale>1.25?1:2);
  });

  stage.addEventListener('pointerdown',event=>{
    if(scale<=1.02) return;
    dragging=true;
    stage.setPointerCapture?.(event.pointerId);
    dragStartX=event.clientX;
    dragStartY=event.clientY;
    originX=x;
    originY=y;
    stage.classList.add('is-dragging');
  });
  stage.addEventListener('pointermove',event=>{
    if(!dragging) return;
    x=originX+(event.clientX-dragStartX);
    y=originY+(event.clientY-dragStartY);
    apply();
  });
  const endDrag=(event)=>{
    if(!dragging) return;
    dragging=false;
    stage.releasePointerCapture?.(event.pointerId);
    stage.classList.remove('is-dragging');
  };
  stage.addEventListener('pointerup',endDrag);
  stage.addEventListener('pointercancel',endDrag);

  document.addEventListener('keydown',event=>{
    if(!viewer.classList.contains('is-open')) return;
    if(event.key==='Escape') close();
    if(event.key==='+'||event.key==='=') setScale(scale+0.25);
    if(event.key==='-') setScale(scale-0.25);
    if(event.key==='0') reset();
  });
})();
