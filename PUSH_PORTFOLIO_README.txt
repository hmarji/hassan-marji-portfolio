HM PORTFOLIO — GITHUB PUSH BUTTON
=================================

INSTALL ONCE
------------
Extract this ZIP and put:

PUSH_PORTFOLIO.bat

inside the MAIN HM Portfolio folder, beside:

index.html
UPDATE_PORTFOLIO.bat
update_portfolio.py

NORMAL IMAGE WORKFLOW
---------------------
1. Add / replace / delete / reorder images.
2. Double-click UPDATE_PORTFOLIO.bat.
3. Open index.html locally and check the website.
4. If everything looks correct, double-click PUSH_PORTFOLIO.bat.
5. Press Y when it asks whether you checked the local site.
6. The BAT automatically runs:
   git add -A
   git commit -m "Update portfolio images"
   git push origin main
7. Open the live website and refresh to verify.

SAFETY
------
- If you answer N, nothing is pushed.
- If there are no changes, it stops safely.
- If Git reports an error, it stops and shows the error.
- It does not modify the website design or gallery code.
