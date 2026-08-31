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