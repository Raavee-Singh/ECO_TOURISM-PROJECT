document.addEventListener('DOMContentLoaded', () => {
  const topbar = document.querySelector('.topbar');
  const navToggle = document.querySelector('.nav-toggle');
  const mainNavigation = document.querySelector('.main-nav');

  const updateNavbar = () => {
    if (topbar) topbar.classList.toggle('is-scrolled', window.scrollY > 24);
  };
  updateNavbar();
  window.addEventListener('scroll', updateNavbar, { passive: true });

  if (topbar && navToggle && mainNavigation) {
    const closeNavigation = () => {
      topbar.classList.remove('menu-open');
      navToggle.setAttribute('aria-expanded', 'false');
      navToggle.setAttribute('aria-label', 'Open navigation menu');
    };

    navToggle.addEventListener('click', () => {
      const expanded = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!expanded));
      navToggle.setAttribute('aria-label', expanded ? 'Open navigation menu' : 'Close navigation menu');
      topbar.classList.toggle('menu-open', !expanded);
    });

    topbar.addEventListener('keydown', (event) => {
      if (event.key !== 'Tab' || !topbar.classList.contains('menu-open')) return;
      const focusable = [...topbar.querySelectorAll('a[href], button:not([disabled]), summary')]
        .filter((element) => element.getClientRects().length);
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });

    mainNavigation.addEventListener('click', (event) => {
      if (event.target instanceof HTMLAnchorElement) closeNavigation();
    });

    document.addEventListener('click', (event) => {
      if (topbar.classList.contains('menu-open') && !topbar.contains(event.target)) closeNavigation();
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeNavigation();
    });

    window.matchMedia('(min-width: 901px)').addEventListener('change', (event) => {
      if (event.matches) closeNavigation();
    });
  }

  const starButtons = document.querySelectorAll('.star-btn');
  const ratingInput = document.getElementById('review-rating');
  if (starButtons.length && ratingInput) {
    const applyStars = (value) => {
      starButtons.forEach((button) => {
        button.classList.toggle('active', Number(button.dataset.value) <= value);
      });
      ratingInput.value = value;
    };
    starButtons.forEach((button) => {
      button.addEventListener('click', () => applyStars(Number(button.dataset.value)));
    });
    applyStars(Number(ratingInput.value) || 5);
  }

  const budgetInputs = document.querySelectorAll('.budget-cost');
  const budgetTotal = document.getElementById('budget-total');
  const rupeeFormatter = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  });
  const updateBudgetTotal = () => {
    const total = Array.from(budgetInputs).reduce((sum, input) => {
      const amount = Number(input.value);
      return sum + (Number.isFinite(amount) && amount > 0 ? amount : 0);
    }, 0);
    if (budgetTotal) budgetTotal.textContent = `Estimated total: ${rupeeFormatter.format(total)}`;
  };
  budgetInputs.forEach((input) => input.addEventListener('input', updateBudgetTotal));
  updateBudgetTotal();

  const today = new Date();
  const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
  document.querySelectorAll('.booking-form').forEach((form) => {
    const startInput = form.querySelector('[name="start_date"]');
    const endInput = form.querySelector('[name="end_date"]');
    if (!startInput || !endInput) return;
    startInput.min = localToday;
    if (form.classList.contains('activity-booking')) {
      form.addEventListener('submit', () => {
        endInput.value = startInput.value;
      });
      return;
    }
    endInput.min = startInput.value || localToday;
    startInput.addEventListener('change', () => {
      endInput.min = startInput.value || localToday;
      if (endInput.value && endInput.value <= startInput.value) endInput.value = '';
    });
  });

  const sceneControl = document.querySelector('.scene-control');
  const sceneTrigger = document.querySelector('.scene-control__trigger');
  const sceneMenu = document.querySelector('.scene-control__menu');
  const sceneChoices = [...document.querySelectorAll('[data-scene-choice]')];
  const scenePlay = document.querySelector('.scene-control__play');
  const sceneImages = [...document.querySelectorAll('[data-scene-image]')];
  const sceneNames = ['elephants', 'macaque'];
  const hero = document.querySelector('.hero-banner');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const saveData = navigator.connection?.saveData === true;
  let currentScene = 'auto';
  let rotationTimer = 0;
  let rotationIndex = 0;
  let heroIsVisible = true;
  let scenePaused = false;
  const assetChecks = new Map();

  const localAssetExists = (url) => {
    if (!assetChecks.has(url)) {
      const check = fetch(url, { method: 'HEAD', cache: 'no-store' })
        .then((response) => response.ok)
        .catch(() => false);
      assetChecks.set(url, check);
    }
    return assetChecks.get(url);
  };

  const updateSceneChoice = (scene) => {
    sceneChoices.forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.sceneChoice === scene));
    });
  };

  const applyScene = (scene) => {
    sceneImages.forEach((image) => {
      image.classList.toggle('is-active', image.dataset.sceneImage === scene);
    });
  };

  const stopSceneRotation = () => {
    window.clearInterval(rotationTimer);
    rotationTimer = 0;
  };

  const startSceneRotation = () => {
    stopSceneRotation();
    if (sceneNames.length < 2 || currentScene !== 'auto' || reducedMotion || saveData || scenePaused) return;
    rotationTimer = window.setInterval(() => {
      if (!heroIsVisible || document.hidden) return;
      rotationIndex += 1;
      applyScene(sceneNames[rotationIndex % sceneNames.length]);
    }, 12000);
  };

  const chooseScene = (choice, persist = true) => {
    currentScene = choice;
    updateSceneChoice(choice);
    if (persist) {
      try {
        window.localStorage.setItem('ecokarnataka-scene', choice);
      } catch {
        // Storage may be disabled; the current page selection still works.
      }
    }
    rotationIndex = 0;
    scenePaused = false;
    if (scenePlay) {
      scenePlay.setAttribute('aria-pressed', 'false');
      scenePlay.textContent = 'Pause movement';
    }
    document.querySelectorAll('.hero-media, .page-backdrop').forEach((layer) => {
      layer.classList.remove('scene-paused');
    });
    applyScene(choice === 'auto' ? sceneNames[0] : choice);
    startSceneRotation();
  };

  if (sceneTrigger && sceneMenu && sceneControl) {
    sceneTrigger.addEventListener('click', () => {
      const expanded = sceneTrigger.getAttribute('aria-expanded') === 'true';
      sceneTrigger.setAttribute('aria-expanded', String(!expanded));
      sceneMenu.hidden = expanded;
      if (!expanded) sceneChoices.find((button) => button.getAttribute('aria-pressed') === 'true')?.focus();
    });

    sceneChoices.forEach((button) => {
      button.addEventListener('click', () => {
        chooseScene(button.dataset.sceneChoice);
        sceneTrigger.setAttribute('aria-expanded', 'false');
        sceneMenu.hidden = true;
        sceneTrigger.focus();
      });
    });

    scenePlay?.addEventListener('click', () => {
      scenePaused = scenePlay.getAttribute('aria-pressed') !== 'true';
      scenePlay.setAttribute('aria-pressed', String(scenePaused));
      scenePlay.textContent = scenePaused ? 'Play movement' : 'Pause movement';
      document.querySelectorAll('.hero-media, .page-backdrop').forEach((layer) => {
        layer.classList.toggle('scene-paused', scenePaused);
      });
      if (!scenePaused) startSceneRotation();
      else stopSceneRotation();
    });

    document.addEventListener('click', (event) => {
      if (!sceneControl.contains(event.target)) {
        sceneTrigger.setAttribute('aria-expanded', 'false');
        sceneMenu.hidden = true;
      }
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        sceneTrigger.setAttribute('aria-expanded', 'false');
        sceneMenu.hidden = true;
        sceneTrigger.focus();
      }
    });
  }

  let savedScene = 'auto';
  try {
    const stored = window.localStorage.getItem('ecokarnataka-scene');
    if (stored && (stored === 'auto' || sceneNames.includes(stored))) savedScene = stored;
  } catch {
    savedScene = 'auto';
  }
  currentScene = savedScene;
  updateSceneChoice(savedScene);
  applyScene(savedScene === 'auto' ? sceneNames[0] : savedScene);

  if ('IntersectionObserver' in window && hero) {
    const observer = new IntersectionObserver((entries) => {
      heroIsVisible = entries.some((entry) => entry.isIntersecting);
      if (heroIsVisible) startSceneRotation();
      else stopSceneRotation();
    }, { threshold: 0.08 });
    observer.observe(hero);
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stopSceneRotation();
    else startSceneRotation();
  });
  startSceneRotation();

  const localImages = [...document.querySelectorAll('[data-local-src]')];
  const loadLocalImage = async (image) => {
    const url = image.dataset.localSrc;
    if (!url || image.dataset.checked) return;
    image.dataset.checked = 'true';
    if (await localAssetExists(url)) image.src = url;
    else image.classList.add('is-unavailable');
  };
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          observer.unobserve(entry.target);
          loadLocalImage(entry.target);
        }
      });
    }, { rootMargin: '220px' });
    localImages.forEach((image) => {
      if (image.loading === 'eager') loadLocalImage(image);
      else imageObserver.observe(image);
    });
  } else {
    localImages.forEach((image) => loadLocalImage(image));
  }
  localImages.forEach((image) => {
    image.addEventListener('error', () => image.classList.add('is-unavailable'), { once: true });
  });

  document.querySelectorAll('img:not(.card-media img)').forEach((image) => {
    image.loading ||= 'lazy';
    image.decoding ||= 'async';
  });
});
