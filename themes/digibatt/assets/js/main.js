import Fuse from 'fuse.js';

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
    const resp = await fetch('/search-index.json');
    if (!resp.ok) return;
    const data = await resp.json();
    fuse = new Fuse(data, {
      keys: [
        { name: 'title',       weight: 0.7 },
        { name: 'description', weight: 0.2 },
        { name: 'section',     weight: 0.1 },
      ],
      threshold: 0.4,
      minMatchCharLength: 2,
      includeScore: true,
    });
  } catch (err) {
    console.error('Search index load failed:', err);
  }
}

function renderResults(results, container) {
  if (!results || results.length === 0) {
    container.innerHTML = '<p class="px-4 py-3 text-sm text-gray-500">No results found.</p>';
  } else {
    container.innerHTML = results
      .slice(0, 8)
      .map(r => `
        <a href="${r.item.url}"
           class="flex flex-col px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-0 no-underline">
          <span class="text-sm font-medium text-gray-900">${r.item.title}</span>
          <span class="text-xs text-gray-500 capitalize">${r.item.section}</span>
        </a>`)
      .join('');
  }
  container.classList.remove('hidden');
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
    renderResults(fuse.search(q), results);
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
      const first = results.querySelector('a');
      if (first) {
        window.location.href = first.href;
      }
    }
  });
}

setupSearch('search-input',       'search-results');
setupSearch('search-input-mobile','search-results-mobile');
setupSearch('search-input-hero',  'search-results-hero');

