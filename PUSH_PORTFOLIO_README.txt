HM PORTFOLIO — UPDATE + PUSH WORKFLOW
====================================

ONE SOURCE OF TRUTH FOR GALLERY IMAGES
--------------------------------------
Selected Work:
  images/selected-work/

Practice:
  images/practice/engineering/
  images/practice/painting/
  images/practice/photography/
  images/practice/graphic-design/
  images/practice/animation/
  images/practice/training/

Knowledge:
  images/knowledge/engineering/
  images/knowledge/painting/
  images/knowledge/photography/
  images/knowledge/graphic-design/
  images/knowledge/animation/
  images/knowledge/training/

Do NOT manually manage images/thumbs/ or images/previews/.
They are generated automatically.

Old names are retired:
  architecture -> engineering
  graphic      -> graphic-design
  education    -> training
  images/originals/ -> retired duplicate source tree

NORMAL IMAGE WORKFLOW
---------------------
1. Add / replace / delete images ONLY in the correct source folder above.
2. Double-click UPDATE_PORTFOLIO.bat.
3. The updater normalizes legacy folders, rebuilds gallery data, creates
   optimized WebP thumbnails/previews and removes unused generated gallery
   derivatives.
4. Open index.html locally and check the website.
5. Run git status and review the changes, especially after the first folder
   normalization.
6. If everything looks correct, double-click PUSH_PORTFOLIO.bat.
7. Press Y when it asks whether you checked the local site.
8. Open the live website and refresh to verify.

SAFETY
------
- UPDATE_PORTFOLIO.bat never pushes automatically.
- Identical legacy duplicate originals are removed during normalization.
- Different files with the same filename are NEVER overwritten; the older
  unique file is preserved with a recovered suffix.
- Local _backup_* folders and Python cache files are ignored by Git.
- The hidden Life Timeline is separate and protected from gallery cleanup.
