# Image chunk evaluation questions

Run each question on `semantic_images` and `hybrid_images`, either in the terminal
(`uv run ask-semantic --images`, `uv run ask-hybrid --images`) or on the Streamlit page
(`uv run streamlit run discovery/image-parsing/app.py`). Fill in the three result columns for
each collection: **Right image** (yes/no), **Wrong image** (any figure that does not answer the
question), **Answer ok** (correct and cited).

Image names are relative to `discovery/image-parsing/images/`.

## Figure questions (an image should come back)

| # | Question | Expected image | Semantic: right / wrong / answer ok | Hybrid: right / wrong / answer ok |
| --- | --- | --- | --- | --- |
| 1 | How does the insulin response to a glucose infusion differ between normal subjects, type 1 and type 2 diabetics? | `Drugs_for_Diabetes-2025-STUDENT_START-_F/p5_5.png` (insulin curves) | | |
| 2 | Show me the feedback loop that controls growth hormone release. | `B7W1_Growth_Hormone_Physiology_STUDENT_S/p5_5.png` (hypothalamus, pituitary, liver diagram) | | |
| 3 | What does somatostatin do to the pituitary somatotrope cells, and how does IGF-1 feed back? | same growth hormone diagram | | |
| 4 | What are the parts of the pituitary gland, and where is it relative to the optic chiasm? | `Pituitary_adenomas_an_overview,_Review_A/p3_0.png` (anatomy, Figure 1) | | |
| 5 | How should an incidental pituitary adenoma be evaluated and managed? | `Pituitary_adenomas_an_overview,_Review_A/p7_3.png` (flowchart, Figure 4) | | |
| 6 | What is the next step if a macroadenoma is found and there is a visual field deficit? | same incidentaloma flowchart | | |
| 7 | What are the segments of the adrenal microlecture series and how long is each? | `Adrenal_Gland_Pathology_Segment_1_-_Over/p3_2.png` (segment table slide) | | |
| 8 | What does a macroadenoma look like on CT? | `Pituitary_adenomas_an_overview,_Review_A/p6_1.png` (CT, Figure 2). Check the picture itself: this one is unverified. | | |
| 9 | How do the action profiles of lispro, regular, NPH and glargine insulin differ over time? | `Drugs_for_Diabetes-2025-STUDENT_START-_F/p24_28.png` (glucose infusion rate by insulin type) | | |
| 12 | Show me an example of Ozempic face. | `Drugs_for_Diabetes-2025-STUDENT_START-_F/p50_62.png` (news article) and `p50_63.png` (before and after portraits). Both only match because the slide text is given to the vision model. | | |

## Controls (no image should come back)

| # | Question | Why | Semantic: wrong image? / answer ok | Hybrid: wrong image? / answer ok |
| --- | --- | --- | --- | --- |
| 10 | What are the side effects of GLP-1? | Text answer from the diabetes lecture, no figure answers it | | |
| 11 | What is the capital of France? | Not in the course, should go to the web, no image | | |
| 13 | What are some herbal supplements for diabetes? | Not covered by a figure; previously returned an unrelated glucagon slide at distance 0.477 | | |

## What to watch for

- **Questions 3 and 6** ask about details inside a figure. If the figure does not come back,
  the strict return rule is missing figures the answer needs.
- **Question 1** used to also bring back the figure from question 9 (`p24_28.png`, distance 0.37
  against 0.22 for the right figure). The image margin should now drop it; if it still comes back,
  record it as a wrong image.
- **Image return rule.** A retrieved image chunk is returned only if its distance is at most
  `IMAGE_MAX_DISTANCE` (0.45) and within `IMAGE_MARGIN` (0.05) of the closest qualifying image.
  Questions 10 and 13 are expected to return no image, and each figure question should return
  only its own figure (question 12 may return both Ozempic slides). Record anything else.
- **Question 11** should return no images at all. Any image here is a wrong image. Questions 10
  and 13 should return none too.
