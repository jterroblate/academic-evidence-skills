> 本版适配说明：当前依赖、证据边界和联网raw-dir要求见 [usage.md](usage.md)。以下英文资料保留上游方法背景；Google Scholar scraper是可选且不完整捕获原始HTTP的渠道，不默认用于可审计发现。web enrichment非强制，取不到的元数据用null；任何DOI/格式有效不能证明claim支持。运行网络例子时每次使用新的raw-dir。

# Example Workflows

Four end-to-end worked examples: building a bibliography for a paper, converting a
list of DOIs, cleaning an existing BibTeX file, and finding and citing seminal papers.

## Example Workflows

### Example 1: Building a Bibliography for a Paper

```bash
# Step 1: Find key papers on your topic
python scripts/search_google_scholar.py "transformer neural networks" \
  --year-start 2017 \
  --limit 50 \
  --output transformers_gs.json

python scripts/search_pubmed.py --raw-dir raw-example-1 "deep learning medical imaging" \
  --date-start 2020 \
  --limit 50 \
  --output medical_dl_pm.json

# Step 2: Extract metadata from search results
python scripts/extract_metadata.py --raw-dir raw-example-2 \
  --input transformers_gs.json \
  --output transformers.bib

python scripts/extract_metadata.py --raw-dir raw-example-3 \
  --input medical_dl_pm.json \
  --output medical.bib

# Step 3: Add specific papers you already know
python scripts/doi_to_bibtex.py --raw-dir raw-example-4 10.1038/s41586-021-03819-2 >> specific.bib
python scripts/doi_to_bibtex.py --raw-dir raw-example-5 10.1126/science.aam9317 >> specific.bib

# Step 4: Combine all BibTeX files
cat transformers.bib medical.bib specific.bib > combined.bib

# Step 5: Format and deduplicate
python scripts/format_bibtex.py combined.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output formatted.bib

# Step 6: Validate
python scripts/validate_citations.py formatted.bib \
  --report validation.json

# Step 7: Review any issues
cat validation.json | grep -A 3 '"errors"'

# Step 8: Use in LaTeX
# \bibliography{final_references}
```

### Example 2: Converting a List of DOIs

```bash
# You have a text file with DOIs (one per line)
# dois.txt contains:
# 10.1038/s41586-021-03819-2
# 10.1126/science.aam9317
# 10.1016/j.cell.2023.01.001

# Convert all to BibTeX
python scripts/doi_to_bibtex.py --raw-dir raw-example-6 --input dois.txt --output references.bib

# Validate the result
python scripts/validate_citations.py references.bib --verbose
```

### Example 3: Cleaning an Existing BibTeX File

```bash
# You have a messy BibTeX file from various sources
# Clean it up systematically

# Step 1: Format and standardize
python scripts/format_bibtex.py messy_references.bib \
  --output step1_formatted.bib

# Step 2: Remove duplicates
python scripts/format_bibtex.py step1_formatted.bib \
  --deduplicate \
  --output step2_deduplicated.bib

# Step 3: Check what is still wrong before sorting
python scripts/validate_citations.py step2_deduplicated.bib \
  --report step3_validation.json

# Step 4: Sort by year
python scripts/format_bibtex.py step2_deduplicated.bib \
  --sort year \
  --descending \
  --output clean_references.bib

# Step 5: Final validation report
python scripts/validate_citations.py clean_references.bib \
  --report final_validation.json \
  --verbose

# Review report
cat final_validation.json
```

### Example 4: Finding and Citing Seminal Papers

```bash
# Find highly cited papers on a topic
python scripts/search_google_scholar.py "AlphaFold protein structure" \
  --year-start 2020 \
  --year-end 2024 \
  --sort-by citations \
  --limit 20 \
  --output alphafold_seminal.json

# Sort within the retrieved sample; this is not a global most-cited ranking
# (the script includes citation counts in JSON)

# Convert to BibTeX
python scripts/extract_metadata.py --raw-dir raw-example-7 \
  --input alphafold_seminal.json \
  --output alphafold_refs.bib

# Verify the selected records and their metadata before citing them
```
