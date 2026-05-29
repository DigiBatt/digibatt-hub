import Fuse from '/js/fuse.min.mjs';

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

// ── Search ────────────────────────────────────────────────────────────────────
let fuse = null;

async function loadSearchIndex() {
  if (fuse) return;
  try {
    const resp = await fetch('/index.json');
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

function renderDropdownResults(results, container) {
  if (!results || results.length === 0) {
    container.innerHTML = '<p class="px-4 py-3 text-sm text-gray-500">No results found.</p>';
  } else {
    container.innerHTML = results
      .slice(0, 8)
      .map(r => `
        <a href="${r.item.url}"
           class="flex flex-col px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-0 no-underline">
          <span class="text-sm font-medium text-gray-900">${r.item.title}</span>
          <span class="text-xs text-gray-500 capitalize">${labelFor(r.item)}</span>
        </a>`)
      .join('');
  }
  container.classList.remove('hidden');
}

function renderPageResults(results, container) {
  if (!results || results.length === 0) {
    container.innerHTML = '<p class="text-gray-500 text-sm">No results found.</p>';
    return;
  }
  container.innerHTML = results
    .map(r => `
      <article class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div class="flex-1 min-w-0">
            <h2 class="text-xl font-semibold text-gray-900 mb-1">${r.item.title}</h2>
            ${r.item.description ? `<p class="text-gray-600 text-sm leading-relaxed">${r.item.description}</p>` : ''}
            <span class="inline-block mt-2 text-xs text-gray-400 capitalize">${labelFor(r.item)}</span>
          </div>
          <a href="${r.item.url}"
             class="shrink-0 inline-flex items-center gap-1 text-sm font-medium text-primary hover:text-secondary no-underline hover:underline">
            View
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </a>
        </div>
      </article>`)
    .join('');
}

function navigateToSearch(query) {
  if (query.trim()) {
    window.location.href = `/search/?q=${encodeURIComponent(query.trim())}`;
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
      pageResults.innerHTML = '<p class="text-gray-500 text-sm">Enter a search term above to find records.</p>';
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

