# Frontend Deployment Guide (Netlify)

You have successfully split your application! You now have a standalone **Frontend Directory** (`frontend/`) and a **Backend API** (your existing Django app).

## 🚀 Step 1: Deploy Backend (Render)
1.  **Commit & Push** your latest changes to GitHub.
2.  Go to your Render Dashboard.
3.  **Redeploy** your existing `musclemeter` Web Service.
    *   This will activate the new API endpoints we added.
    *   Ensure `CORS_ALLOWED_ORIGINS` in `settings.py` includes your Netlify URL (once you have it). For now, `CORS_ALLOW_ALL_ORIGINS = True` allows everything.

## 🎨 Step 2: Deploy Frontend (Netlify)

### Option A: Drag & Drop (Easiest)
1.  Go to [Netlify Drop](https://app.netlify.com/drop).
2.  **Drag and Drop** the entire `frontend` folder from your computer into the browser.

### Option B: Connect to GitHub (Recommended for Updates)
Since you pushed your code to GitHub, you can connect Netlify to it. This way, **every time you push changes, Netlify updates your site automatically.**

1.  Log in to Netlify and click **"Add new site"** -> **"Import from existing project"**.
2.  Select **GitHub** and authorize it.
3.  Pick your repository (`musclemeter`).
4.  **CRITICAL CONFIGURATION:**
    *   **Base directory:** `frontend`  <-- You MUST set this!
    *   **Publish directory:** `frontend` (or leave blank if specific to build settings, but since it's static, usually just `frontend` acts as root).
    *   **Build command:** (Leave empty, it's just HTML/JS).
5.  Click **Deploy Site**.

## 🔗 Step 3: Connect Frontend to Backend
1.  Open `frontend/config.js` on your computer.
2.  Change `API_URL` to your **Render Backend URL**:
    ```javascript
    const config = {
        API_URL: 'https://your-render-app.onrender.com/api', 
    };
    ```
3.  Save the file.
4.  **Re-upload** the `frontend` folder to Netlify (or set up GitHub deployment for the `frontend` folder).

## 🎉 Done!
Your Frontend is now on Netlify, talking to your Backend on Render.
