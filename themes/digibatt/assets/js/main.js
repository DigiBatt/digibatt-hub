import Fuse from './fuse.min.mjs';

// ── Hamburger menu toggle ─────────────────────────────────────────────────────
const menuToggle = document.getElementById('menu-toggle');
const mobileMenu = document.getElementById('mobile-menu');
const menuIcon   = document.getElementById('menu-icon');
const closeIcon  = document.getElementById('close-icon');

if (menuToggle && mobileMenu) {
  menuToggle.addEventListener('click', () => {
    const isOpen = !mobileMenu.classList.contains('hidden');
    mobileMenu.classList.toggle('hidden', isOpen);
    menuIcon.classList.toggle('hidden', !isOpen);
    closeIcon.classList.toggle('hidden', isOpen);
    menuToggle.setAttribute('aria-expanded', String(!isOpen));
  });
}

// ── Mobile sub-menu toggles ───────────────────────────────────────────────────
document.querySelectorAll('.mobile-submenu-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const submenu = btn.nextElementSibling;
    const chevron = btn.querySelector('.mobile-chevron');
    const isOpen = !submenu.classList.contains('hidden');
    submenu.classList.toggle('hidden', isOpen);
    chevron.classList.toggle('rotate-180', !isOpen);
    btn.setAttribute('aria-expanded', String(!isOpen));
  });
});

// ── Search ────────────────────────────────────────────────────────────────────
const SEARCH_INDEX_URL = document.querySelector('meta[name="search-index-url"]')?.content || '/index.json';
const SEARCH_PAGE_URL  = document.querySelector('meta[name="search-page-url"]')?.content  || '/search/';

let fuse = null;

async function loadSearchIndex() {
  if (fuse) return;
  try {
    const resp = await fetch(SEARCH_INDEX_URL);
    if (!resp.ok) return;
    const data = await resp.json();
    fuse = new Fuse(data, {
      keys: [
        { name: 'title',       weight: 0.7 },
        { name: 'description', weight: 0.2 },
        { name: 'category',    weight: 0.05 },
        { name: 'subcategory', weight: 0.05 },
      ],
      threshold: 0.4,
      minMatchCharLength: 2,
      includeScore: true,
    });
  } catch (err) {
    console.error('Search index load failed:', err);
  }
}

function labelFor(item) {
  const parts = [];
  if (item.category)    parts.push(item.category.replace(/-/g, ' '));
  if (item.subcategory) parts.push(item.subcategory.replace(/-/g, ' '));
  return parts.join(' › ');
}

// Return a safe URL: only allow relative paths and http(s) URLs.
function safeUrl(url) {
  if (!url) return '#';
  if (url.startsWith('/') || url.startsWith('https://') || url.startsWith('http://')) return url;
  return '#';
}

function renderDropdownResults(results, container) {
  container.textContent = '';
  if (!results || results.length === 0) {
    const p = document.createElement('p');
    p.className = 'px-4 py-3 text-sm text-gray-500';
    p.textContent = 'No results found.';
    container.appendChild(p);
  } else {
    results.slice(0, 8).forEach(r => {
      const a = document.createElement('a');
      a.href = safeUrl(r.item.url);
      a.className = 'flex flex-col px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-0 no-underline';

      const title = document.createElement('span');
      title.className = 'text-sm font-medium text-gray-900';
      title.textContent = r.item.title;

      const label = document.createElement('span');
      label.className = 'text-xs text-gray-500 capitalize';
      label.textContent = labelFor(r.item);

      a.appendChild(title);
      a.appendChild(label);
      container.appendChild(a);
    });
  }
  container.classList.remove('hidden');
}

// SVG path for the "chevron right" arrow used in result cards.
const CHEVRON_PATH = 'M9 5l7 7-7 7';

function renderPageResults(results, container) {
  container.textContent = '';
  if (!results || results.length === 0) {
    const p = document.createElement('p');
    p.className = 'text-gray-500 text-sm';
    p.textContent = 'No results found.';
    container.appendChild(p);
    return;
  }
  results.forEach(r => {
    const article = document.createElement('article');
    article.className = 'bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200';

    const row = document.createElement('div');
    row.className = 'flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3';

    const body = document.createElement('div');
    body.className = 'flex-1 min-w-0';

    const h2 = document.createElement('h2');
    h2.className = 'text-xl font-semibold text-gray-900 mb-1';
    h2.textContent = r.item.title;
    body.appendChild(h2);

    if (r.item.description) {
      const desc = document.createElement('p');
      desc.className = 'text-gray-600 text-sm leading-relaxed';
      desc.textContent = r.item.description;
      body.appendChild(desc);
    }

    const cat = document.createElement('span');
    cat.className = 'inline-block mt-2 text-xs text-gray-400 capitalize';
    cat.textContent = labelFor(r.item);
    body.appendChild(cat);

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'w-3.5 h-3.5');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('viewBox', '0 0 24 24');
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('stroke-linejoin', 'round');
    path.setAttribute('stroke-width', '2');
    path.setAttribute('d', CHEVRON_PATH);
    svg.appendChild(path);

    const link = document.createElement('a');
    link.href = safeUrl(r.item.url);
    link.className = 'shrink-0 inline-flex items-center gap-1 text-sm font-medium text-primary hover:text-secondary no-underline hover:underline';
    link.textContent = 'View';
    link.appendChild(svg);

    row.appendChild(body);
    row.appendChild(link);
    article.appendChild(row);
    container.appendChild(article);
  });
}

function navigateToSearch(query) {
  if (query.trim()) {
    window.location.href = SEARCH_PAGE_URL + '?q=' + encodeURIComponent(query.trim());
  }
}

function setupSearch(inputId, resultsId) {
  const input   = document.getElementById(inputId);
  const results = document.getElementById(resultsId);
  if (!input || !results) return;

  input.addEventListener('focus', loadSearchIndex);

  input.addEventListener('input', async () => {
    const q = input.value.trim();
    if (!q) { results.classList.add('hidden'); return; }
    await loadSearchIndex();
    if (!fuse) return;
    renderDropdownResults(fuse.search(q), results);
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !results.contains(e.target)) {
      results.classList.add('hidden');
    }
  });

  // Keyboard navigation
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      results.classList.add('hidden');
      input.blur();
    } else if (e.key === 'Enter') {
      navigateToSearch(input.value);
    }
  });
}

setupSearch('search-input',       'search-results');
setupSearch('search-input-mobile','search-results-mobile');
setupSearch('search-input-hero',  'search-results-hero');

// ── Search results page ───────────────────────────────────────────────────────
const pageInput   = document.getElementById('search-input-page');
const pageResults = document.getElementById('search-results-page');

if (pageInput && pageResults) {
  const params = new URLSearchParams(window.location.search);
  const initialQuery = params.get('q') || '';

  async function runPageSearch(q) {
    await loadSearchIndex();
    if (!fuse) return;
    if (!q.trim()) {
      pageResults.textContent = '';
      const hint = document.createElement('p');
      hint.className = 'text-gray-500 text-sm';
      hint.textContent = 'Enter a search term above to find records.';
      pageResults.appendChild(hint);
      return;
    }
    renderPageResults(fuse.search(q), pageResults);
  }

  if (initialQuery) {
    pageInput.value = initialQuery;
    runPageSearch(initialQuery);
  }

  pageInput.addEventListener('input', () => {
    const q = pageInput.value;
    const url = new URL(window.location);
    if (q.trim()) {
      url.searchParams.set('q', q.trim());
    } else {
      url.searchParams.delete('q');
    }
    history.replaceState(null, '', url);
    runPageSearch(q);
  });

  pageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') pageInput.blur();
  });
}

