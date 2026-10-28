# UICOMP Curriculum AI Assistant

A chat web app for the UICOMP medical-education assistant. Users sign up or log in, start chats, and see their past conversations. Accounts, chats and messages are stored in **Supabase**, and each user only sees their own chats. The assistant's replies are placeholder text for now; the real AI is not connected yet.

## What you need

- **Node.js 20.19 or newer** (22.12+ also works). Check with `node --version`. Download from https://nodejs.org.
- **A Supabase project** with its Project URL and anon (public) key. They're under Supabase Dashboard → Project Settings → API. Use the **anon** key, never the `service_role` key.

## Set up (first time only)

1. Open a terminal in this folder (the one with `package.json`).
2. Install the packages:

   ```
   npm install
   ```

3. Create a file named **`.env.local`** in this folder with your Supabase keys:

   ```
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   ```

   Don't share this file or upload it to GitHub.

4. Set up the database (once per Supabase project). In Supabase Dashboard → **SQL Editor**, paste the contents of [`supabase/setup.sql`](supabase/setup.sql) and click **Run**. This creates the `threads` and `messages` tables and the privacy rules that keep each user's chats to themselves. It's safe to run again.

## Run it

```
npm run dev
```

Then open **http://localhost:5173** in your browser. Press `Ctrl + C` in the terminal to stop.

While it's running, saving a file updates the page automatically.

## Other commands

| Command | What it does |
| --- | --- |
| `npm run build` | Checks everything compiles and writes a finished copy to `dist/` |
| `npm run preview` | Serves the `dist/` copy so you can look at it (run `npm run build` first) |

## If something goes wrong

- **The page says "Supabase keys missing":** `.env.local` is missing, or its URL isn't a valid `http(s)://` address. Create or fix it as shown above, then stop the server and run `npm run dev` again. Vite only reads `.env.local` when it starts.
- **The page is completely blank:** open the browser console (F12, then the Console tab) and read the red error. Also, don't open `dist/index.html` by double-clicking it; that always shows a blank page. Use `npm run dev`, or `npm run build` followed by `npm run preview`.
- **"Failed to resolve import @supabase/supabase-js":** run `npm install`.
- **PowerShell says "running scripts is disabled":** use Command Prompt (`cmd`), or type `npm.cmd install` and `npm.cmd run dev`.
- **Port 5173 is busy:** Vite picks the next free port and prints the address. Use that one.
- **Chats don't save, or the history stays empty:** make sure `supabase/setup.sql` was run in the project's SQL Editor (step 4).
- **"Invalid login credentials":** wrong email or password. Logging in needs the account's **email**; usernames aren't supported by Supabase.
- **Sign-up says "Check your email to confirm it":** the Supabase project requires new users to confirm their email. Click the link in the email, then log in. For testing, the project owner can turn off **Confirm email** in Supabase's Authentication settings for the Email provider.
- **The font looks different:** Plus Jakarta Sans loads from Google Fonts and needs internet.

## Good to know

- **You stay logged in.** Supabase remembers the session in the browser, so refreshing the page keeps you signed in and your chats are still there. Use **Log out** in the sidebar to sign out.
- **Sign-up checks:** passwords must match and be at least 8 characters. The full name is saved with the account.
- **"Forgot password?"** is only a link for now.
- **Placeholder replies:** the assistant's reply is fake text that appears one second after you send a message.
- **Desktop layout:** the design is for desktop width (1280px wide in the Figma).

For a plain-language tour of the code, see [HOW_IT_WORKS.md](../HOW_IT_WORKS.md) (one folder up, next to this `UICOM` folder).
