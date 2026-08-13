# Media Pipeline V1

## Architecture

The importer is an explicit, offline publishing step—not part of the site build. Untrusted ZIPs may be placed in the ignored `media-source/` directory. `tools/process_media_pack.py` writes only optimized WebP files under `images/<type>/<slug>/`, a production manifest at `data/media/<slug>.json`, and a tooling-only contact sheet at `data/media/previews/<slug>-contact-sheet.jpg`. `tools/media_utils.py` holds reusable security and image helpers; `tools/validate_media.py` audits committed output.

`prepare_deploy.py` stages `images/**` and public `data/media/*.json`. It deliberately excludes ZIPs, source images, previews, caches, and temporary directories.

## Installation

Use Python 3.10 or newer and install the bounded media dependency separately:

```bash
python3 -m pip install -r requirements-media.txt
```

Pillow decodes JPEG, PNG, and WebP. HEIC is intentionally unsupported because its optional native/plugin dependency is not reliably available; convert HEIC before import or add a reviewed decoder in a later pipeline version.

## CLI

```bash
python3 tools/process_media_pack.py \
  --input media-source/lumier.zip \
  --slug lumiere-evergreen \
  --type project
```

Types are `project`, `amenity`, `editorial`, `listing`, and `shared`. `--output` is allowed only below this repository's `images/` tree. Use `--dry-run` to decode, deduplicate, resize, and report without writing. Use `--force` to atomically replace an existing pack. Without it, existing output is protected. Member ordering, sequential names, JSON ordering, dimensions, and encoder settings are stable, so the same environment and ZIP produce the same result.

## Formats, normalization, and optimization

Accepted extensions are `.jpg`, `.jpeg`, `.png`, and `.webp`. Every candidate is fully decoded, EXIF-orientation corrected, converted to RGB, and stripped of metadata. Transparent pixels are composited over white. Corrupt images are logged rather than stopping other candidates.

Four uncropped, aspect-preserving WebP variants are produced without upscaling:

| Variant | Maximum width |
| --- | ---: |
| `hero` | 1920 px |
| `content` | 1400 px |
| `card` | 900 px |
| `thumb` | 560 px |

All variants use WebP quality 84 and Pillow encoder method 6. This favors property-image detail over aggressive compression. A small source stays at its native dimensions (although each named variant remains available for simple consumers). The run summary reports combined variant bytes and source savings; warnings flag small and extremely narrow images.

## Naming and duplicate strategy

Slugs and output filenames contain lowercase ASCII letters, digits, and hyphens. Assets are deterministically named `<slug>-01-hero.webp`, `<slug>-01-content.webp`, and so on. Original filenames never become output paths.

The first duplicate pass hashes normalized RGB pixels plus dimensions with SHA-256, catching byte-identical visual content after metadata/orientation normalization. A dependency-free 64-bit difference hash then catches conservative near-duplicates (Hamming distance at most 2), including many resaves. The first file in stable semantic/name order wins. Rejected duplicates remain documented in the manifest with `originalFilename`, `duplicateOf`, and `strategy`; they are not published.

## Manifest schema and curation

The root contains `schemaVersion`, `slug`, `type`, `variantWidths`, `webpQuality`, `assets`, and `duplicates`. Each asset contains stable `id`, `filename`, root-relative `src`, four `variants`, hero `width`/`height`/`bytes`, `aspectRatio`, normalized `sha256`, `perceptualHash`, conservative `role`, blank `alt` and `caption`, `originalFilename`, `featured`, and `sortOrder`.

The default role is `general`. Only unambiguous filename tokens infer `pool`, `lobby`, `layout`, `map`, `construction`, `interior`, `exterior`, or `landscape`; the pipeline never guesses image subject matter. Curators may set `hero`, `amenity`, or other supported roles and should write concise descriptive alt text. Do not add search keywords. This metadata supports future homepage selection and project hero/gallery/amenity/layout views without coupling the processor to a page.

## Security and quality guards

ZIP content is treated as hostile. The reader never extracts members to disk and rejects absolute/traversal paths, backslash traversal, symlinks, executable-mode entries, encryption, hidden/macOS metadata, unsupported media, nested archives, oversized members, excessive entries, and over 1 GB of declared uncompressed data. It never executes or imports ZIP content. Source paths and local absolute paths are absent from manifests.

The command fails for an invalid slug, bad ZIP, no valid unique image, output outside `images/`, existing output without `--force`, or duplicate generated names. It warns above 100 MB/500 candidate images and for suspect dimensions. The validator checks JSON shape, IDs, URL-safe local paths, missing files, duplicate outputs, hero dimensions, and leaked developer paths:

```bash
python3 tools/validate_media.py
python3 tools/validate_media.py --slug lumiere-evergreen
```

## Contact sheet and Codex workflow

The contact sheet labels each thumbnail by index, deterministic output base name, and inferred role. It is intentionally not deployed.

1. The user uploads `lumier.zip`; no manual extraction or renaming is needed.
2. Codex moves/leaves it in ignored workspace storage and runs the importer.
3. Codex opens `data/media/previews/lumiere-evergreen-contact-sheet.jpg`.
4. Codex selects hero, gallery, amenities, and article candidates.
5. Codex reviews/edits `role`, `alt`, `caption`, `featured`, and `sortOrder` without changing generated paths.
6. Pages consume manifest paths as required.
7. Codex runs media and site validation, then commits only optimized images and the production manifest.
8. Codex pushes the branch and opens a pull request; it does not merge automatically.

## Remote Google Drive Import

Public Google Drive folders can be ingested without a local clone. The importer uses
`gdown`'s maintained public-folder downloader (no Google credentials or private API
key), keeps all remote files and its temporary ZIP outside the repository, and then
passes an approved image-only ZIP to Media Pipeline V1:

```bash
python3 tools/import_drive_media.py \
  --folder-id 1IePvNlBcINOwjuNsDZMw7P5rRuMeFlSc \
  --slug lumiere-evergreen \
  --type project
```

The remote boundary accepts only top-level `.jpg`, `.jpeg`, `.png`, and `.webp`
files whose decoded Pillow format matches the extension. It rejects unsafe/control
character names, nested paths, links, empty/corrupt/mismatched files, unsupported
documents, and folders with any unsupported file. Defaults are at most 200 images,
50 MB per image, and 500 MB total; `--max-files`, `--max-file-mb`, and
`--max-total-mb` can adjust bounded limits. Originals, downloads, and the temporary
ZIP are deleted on success or failure. The existing processor performs its own
second validation, normalization, deduplication, and WebP generation.

For the no-terminal workflow:

1. Upload the source photos to a Google Drive folder.
2. Share the folder as **Anyone with the link / Viewer**.
3. Open **GitHub Actions → Import Media → Run workflow**.
4. Enter the folder ID, slug, and media type; optionally supply a new branch name.
5. The job validates, builds, creates and pushes a new branch, then opens a pull
   request for review. It never commits directly to `main`.
6. Review curation and generated pages, then merge the pull request manually.

The action has only `contents: write` and `pull-requests: write` permissions. It
stages optimized WebP files, the production manifest, and generated HTML explicitly;
source images, contact sheets, temporary files, and deployment output are rejected.
For project manifests, the existing profile builder deterministically chooses the
first asset when no reviewed hero is marked, uses other assets for the gallery, and
uses the card variant on the project hub. Alt and curation fields remain blank/editable
rather than being fabricated by the remote job.

## Troubleshooting

- **Output exists:** inspect it, then rerun with `--force` only when replacement is intended.
- **No valid images:** check supported formats and whether files really decode; extension alone is insufficient.
- **Image missing:** rerun import or restore the committed WebP, then run the slug validator.
- **Unexpected duplicate:** review `duplicates` and source files. The intentionally strict dHash threshold can be changed only with fixture coverage.
- **Large ZIP warning:** processing may be slow; the hard member/count/uncompressed limits still protect the workspace.
- **HEIC:** export JPEG/PNG/WebP first; there is no silent HEIC fallback.
