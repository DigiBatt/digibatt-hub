+++
title = 'Submit a Resource'
date = 2024-01-14T07:07:07+01:00
draft = false
+++

## Submit a Resource to the DigiBatt Hub

Have a battery modelling tool, dataset, publication, database or tutorial to share? We welcome contributions from the community.

### How to Submit

1. Click the button below (or use the **Submit** link in the navigation).
2. Choose the **Submit a Record** issue template.
3. Select the record type (software / publication / dataset / database / tutorial).
4. Paste a JSON object describing your resource — see the [schemas](https://github.com/DigiBatt/digibatt-hub/tree/main/schemas) for the required fields.
5. Submit the issue. A maintainer will review and add the record.

{{< btn href="https://github.com/DigiBatt/digibatt-hub/issues/new/choose" target="_blank" >}}
  Open Submission Form →
{{< /btn >}}

### JSON Schemas

Each record type has a JSON schema describing the expected fields. Schemas are available in the repository:

| Type | Schema |
|---|---|
| Software | [schemas/software.json](https://github.com/DigiBatt/digibatt-hub/blob/main/schemas/software.json) |
| Publication | [schemas/publication.json](https://github.com/DigiBatt/digibatt-hub/blob/main/schemas/publication.json) |
| Dataset | [schemas/dataset.json](https://github.com/DigiBatt/digibatt-hub/blob/main/schemas/dataset.json) |
| Database | [schemas/database.json](https://github.com/DigiBatt/digibatt-hub/blob/main/schemas/database.json) |
| Tutorial | [schemas/tutorial.json](https://github.com/DigiBatt/digibatt-hub/blob/main/schemas/tutorial.json) |
