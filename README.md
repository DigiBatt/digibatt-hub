# DigiBatt Hub

A searchable knowledge hub for battery research resources, built with [Hugo](https://gohugo.io/) and [Tailwind CSS](https://tailwindcss.com/). It aggregates datasets, publications, software, tutorials, and other resources across several battery research categories.

---

## Features

- Full-text fuzzy search powered by [Fuse.js](https://www.fusejs.io/)
- Categories: Cyclic Testing, Data Repositories, Data Standardisation, Simulation & Parameterisation, System-Level Testing
- Record types: Dataset, Publication, Software, Tutorial, Other
- Mobile-responsive layout
- Auto-generated JSON search index via Hugo

---

## Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) v0.120+
- [Node.js](https://nodejs.org/) v18+
- npm v9+

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/digibatt-hub.git
   cd digibatt-hub
   ```

2. **Install Node dependencies** (Tailwind CSS and build tools)

   ```bash
   npm install
   ```

3. **Install Hugo** (if not already installed)

   ```bash
   # macOS via Homebrew
   brew install hugo
   ```

---

## Running Locally

Start the Hugo development server with Tailwind CSS watching for changes:

```bash
# In one terminal — watch and build Tailwind
npm run dev

# In another terminal — serve the Hugo site
hugo server
```

Or, if your `package.json` has a combined script:

```bash
npm start
```

The site will be available at [http://localhost:1313](http://localhost:1313).

> **Note:** Hugo must be run with the `--disableFastRender` flag if you notice stale CSS:
> ```bash
> hugo server --disableFastRender
> ```

### Building for Production

```bash
npm run build   # builds Tailwind CSS (minified)
hugo --minify   # builds the static site into /public
```

---

## Project Structure

```
digibatt-hub/
├── content/              # Markdown content (records, pages)
│   ├── cyclic-testing/
│   ├── data-repositories/
│   ├── data-standardisation/
│   ├── simulation-and-parameterisation/
│   └── system-level-testing/
├── themes/digibatt/      # Custom Hugo theme (layouts, assets)
├── schemas/              # JSON schemas for record types
├── assets/python/        # Helper scripts for importing records
├── data/                 # Raw and converted JSON data
└── hugo.toml             # Hugo configuration
```

---

## Adding New Records

Records are Markdown files with structured front matter. Each record belongs to a **category** (e.g. `cyclic-testing`) and a **type** (e.g. `dataset`, `publication`, `software`, `tutorial`, `other`).

### Option 1 — Submit via GitHub Issue (recommended for non-developers)

1. Go to the [Issues tab](../../issues) and select **"Submit a Record"**.
2. Fill in the form with the resource details (title, URL, description, category, etc.).
3. A maintainer will review and add it to the hub.

### Option 2 — Submit via Pull Request

1. **Fork** the repository and create a new branch:

   ```bash
   git checkout -b add/my-new-record
   ```

2. **Create a new content file** using a Hugo archetype:

   ```bash
   hugo new cyclic-testing/dataset/my-dataset.md
   # or
   hugo new data-standardisation/software/my-tool.md
   ```

3. **Edit the generated file** and fill in the front matter. Example for a dataset:

   ```yaml
   ---
   title: "My Battery Dataset"
   date: 2026-06-12
   description: "A short description of the resource."
   url: "https://doi.org/10.xxxx/xxxxx"
   category: "cyclic-testing"
   subcategory: "dataset"
   tags: ["lithium-ion", "NMC"]
   draft: false
   ---
   ```

4. **Validate** your file against the appropriate JSON schema in `/schemas/`.

5. **Preview locally** with `hugo server`.

6. **Open a Pull Request** against `main`. A maintainer will review and merge it.

---

## Record Schemas

JSON schemas for each record type are in the `/schemas/` directory:

| Type        | Schema file              |
|-------------|--------------------------|
| Dataset     | `schemas/dataset.json`   |
| Publication | `schemas/publication.json` |
| Software    | `schemas/software.json`  |
| Tutorial    | `schemas/tutorial.json`  |
| Other       | `schemas/other.json`     |

---

## Funding

This project has received funding from the European Union.

![Funded by the European Union](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/320px-Flag_of_Europe.svg.png)

---

## License

See [LICENSE](./LICENSE) for details.