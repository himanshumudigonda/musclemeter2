# Frontend Deployment Guide (Netlify)

You have successfully split your application! You now have a standalone **Frontend Directory** (`frontend/`) and a **Backend API** (your existing Django app).

## 🚀 Step 1: Deploy Backend (Render)
1.  **Commit & Push** your latest changes to GitHub.
2.  Go to your Render Dashboard.
3.  **Redeploy** your existing `musclemeter` Web Service.
    *   This will activate the new API endpoints we added.
    *   Ensure `CORS_ALLOWED_ORIGINS` in `settings.py` includes your Netlify URL (once you have it). For now, `CORS_ALLOW_ALL_ORIGINS = True` allows everything.

## 🎨 Step 2: Deploy Frontend (Netlify)
1.  Go to [Netlify Drop](https://app.netlify.com/drop).
2.  **Drag and Drop** the entire `frontend` folder from your computer into the browser.
3.  Netlify will instantly deploy it and give you a URL (e.g., `https://brave-musclemeter-12345.netlify.app`).

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
