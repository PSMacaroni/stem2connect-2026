# Hosting on Streamlit Community Cloud (steps for the owner)

The app downloads its models from the GitHub release `v1` at startup (`src/molscreen/assets.py`), so the repo
must be public (it is, since 2026-11-04) and the release must exist (it does: 212 files, 178,693,014 bytes,
zip SHA-256 `b9f940ef0d1a05994a2673027e9c340bd60247213a18ac9ddda85782cafa276b`).

## Deploy (about 10 minutes, once)
1. Open https://share.streamlit.io and click **Sign in with GitHub**. Allow it to see your repositories.
2. Click **Create app** (or **New app**), then **Deploy a public app from GitHub**.
3. Fill the form: Repository `PSMacaroni/stem2connect-2026`, Branch `main`, Main file path `app.py`.
   App URL: pick a short name, for example `molecule-screening-workbench`.
4. Click **Advanced settings**. Python version: **3.12**. In **Secrets**, paste exactly one line:
   `MOLSCREEN_MODELS_SHA256 = "b9f940ef0d1a05994a2673027e9c340bd60247213a18ac9ddda85782cafa276b"`
   (no other secrets exist; the download is anonymous).
5. Click **Deploy**. The first build installs `requirements.txt` (a few minutes) and then downloads the 179 MB
   bundle (one more minute). Watch the log on the right: it should print `models: zip SHA-256 matches` and
   `models: 212 files verified`.

## Check it worked
1. Open the app URL in a private browser window (signed out).
2. Pick a target in the sidebar, click **Example**, and see three molecules with probabilities and the drawn
   nearest actives. The "Cell lines" and "Safety flags" tabs do the same with their Example buttons.
3. If the page shows "Could not get the trained models", open **Manage app** > logs: the URL or the SHA-256 in
   the secret is wrong, or the release is missing.

## Keep it alive
- Free apps sleep after 12 idle hours; a visitor wakes them in about a minute. Open the URL yourself the morning
  of judging (Nov 22) and before Demo Day (Nov 24).
- Memory ceiling is about 2.7 GB; the three bundles together load well under that, but do not add bigger models.
- A new release (`v2`) needs `TAG` in `src/molscreen/assets.py` changed and the secret updated, then **Reboot app**.
