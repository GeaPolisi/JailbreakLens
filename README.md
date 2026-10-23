# JailbreakLens

A browser-based tool and the supplementary files for the MSc thesis below. Code is released under the MIT licence (see LICENSE). Use it only for AI-safety research and respect the terms of the model provider. Enter your own API key in the tool; no key is stored in this repository.

## Thesis

Thesis: "Behavioral Jailbreak Attacks Against Large Language Models: Taxonomy and Resistance Analysis"
Author: Gea Polisi, MSc Artificial Intelligence, University of New York Tirana (UNYT), October 2026
Advisor: Evis Trandafili

## Contents

| Folder | File | Description |
|---|---|---|
| tool/ | JailbreakLens_v4.html | The testing tool: one HTML file, runs in a browser, calls the Groq API with the user's own key (no key is included). |
| tool/ | test_v4.py | Scripted browser test of the tool against a simulated API. |
| data/ | prompts_used.csv | The 89 analysed prompts (id, category, prompt). |
| data/ | prompts_provenance.csv | Source of each prompt (Hugging Face, PAIR, GCG) and whether a template was completed. |
| data/ | results_verdicts_no_response_text.csv | One row per prompt-model pair (267): model, finish reason, judge verdict, strict and lenient flags. |
| labels/ | claude_annotator_labels_responses.csv | LLM annotator (Claude Sonnet 5.5) labels of the 52 validation responses. These are AI labels. |
| labels/ | claude_annotator_labels_prompts.csv | LLM annotator relabelling of the 89 prompts. These are AI labels. |
| labels/ | author_labels_16_responses.csv | The author's labels of the 16 additional COMPLIED responses. |
| labels/ | labelling_key_responses.csv | Sample key (which responses were in the stratified sample or the COMPLIED check). |
| code/ | stats.py, an1.py, an2.py, an4.py | Analysis scripts (Wilson intervals, permutation and McNemar tests, kappa). File paths inside need adjusting to run elsewhere. |
| analysis_output/ | table_*.csv, stats.json | Output tables used in Chapter 4. |

## What is not included, and why

* Raw model responses are not published. They contain harmful material, and the thesis (Section 3.5) states that they are stored by the author only and used for classification and analysis. They are available to the examiners on request.
* One prompt (HYP-03) was removed from the sample after the run because it should have been excluded by the content filter (thesis Section 4.1). It is not reproduced anywhere in these files.
* No API key is included.

## Data sources and licences

* llm-semantic-router/jailbreak-detection-dataset, Hugging Face (Apache-2.0).
* JailbreakBench attack artifacts, PAIR and GCG (MIT; Chao et al., 2024).

## How the experiment was run

JailbreakLens v4 sent each prompt once to openai/gpt-oss-20b, allam-2-7b and qwen/qwen3.8-27b through the Groq API (no system prompt, temperature 0, 1,024 or 2,048 max tokens) and judged each response with openai/gpt-oss-120b (judge prompt in Appendix C of the thesis).

## AI use

The thesis code and analysis were developed with the help of Claude Sonnet 5.5 (Anthropic). See the AI Declaration Statement and Appendix A of the thesis.
