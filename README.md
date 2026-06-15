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

- [Hugo](https://gohugo.io/installation/) v0.120+
- [Node.js](https://nodejs.org/) v18+
- npm v9+

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/DigiBatt/digibatt-hub.git
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

Start the Hugo development server:

```bash
# In the terminal — serve the Hugo site
hugo server
```

The site will be available at [http://localhost:1313](http://localhost:1313).

---

## Project Structure

```
digibatt-hub/
├── content/              # Markdown content (Category pages)
│   ├── cyclic-testing/
│   ├── data-repositories/
│   ├── data-standardisation/
│   ├── simulation-and-parameterisation/
│   ├── system-level-testing/
│   └── records/          # Markdown content (Record pages)
├── themes/digibatt/      # Custom Hugo theme (layouts, assets)
├── schemas/              # JSON schemas for record types
├── assets/python/        # Helper scripts for importing records
├── data/                 # Raw and converted JSON data
└── hugo.toml             # Hugo configuration
```

---

## Adding New Records

Records are Markdown files with structured front matter. Each record can have multiple **categories** (e.g. `cyclic-testing`) and a single **type** (e.g. `dataset`, `publication`, `software`, `tutorial`, `other`).

### Option 1 — Submit via GitHub Issue (recommended for non-developers)

1. Go to the [Issues tab](../../issues) and select **"Submit a Record"**.
2. Fill in the form with the resource details (title, URL, description, category, etc.).
3. A maintainer will review and add it to the hub.

### Option 2 — Submit .md file via Pull Request

1. **Fork** the repository and create a new branch:

   ```bash
   git checkout -b add/my-new-record
   ```
2. Create a new .md file for the record and place it in `content/records/`

5. **Preview locally** with `hugo server`.

6. **Open a Pull Request** against `main`. A maintainer will review and merge it.



---

## Creating a new record

There are some utilities available in the repo to make it easier to generate new records. 


### Converting .json to .md via python script.

1. **Create a .json file** from the correct json template in `schemas/json_templates/`

2. Place the file in `data/submitted/`

3. **Convert to a .md file** by running `assets/python/convert_dbjson_to_md.py`

This should validate against the correct schema, create a new .md file and place it into the `content/records` folder.

### Creating .md file via hugo archetypes

1. **Create a new file** from the correct hugo archetype (found in `archetypes/`)

   ```bash
   # e.g.
   hugo new -k dataset records/my-dataset.md
   # or
   hugo new -k software records/my-tool.md
   ```

3. **Edit the generated file** and fill in the front matter and put the description in the main file content.

4. **Validate** your file against the appropriate JSON schema in `/schemas/`.



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

---

## License

Website code is licenced under GPL3. See [LICENSE](./LICENSE) for details.