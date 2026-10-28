import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { MissingKeysNotice } from './components/MissingKeysNotice.jsx'

const root = createRoot(document.getElementById('root'))

// True if the value is a web address starting with http:// or https://
// (the same check Supabase does before it starts).
function isWebAddress(value) {
  try {
    const url = new URL(value)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

// Supabase needs these two values from .env.local. Without them it crashes
// while starting and the page stays blank, so show a clear message instead.
const hasSupabaseKeys =
  isWebAddress(import.meta.env.VITE_SUPABASE_URL) && Boolean(import.meta.env.VITE_SUPABASE_ANON_KEY)

if (hasSupabaseKeys) {
  // The app is loaded only after the check, because loading it starts Supabase.
  import('./App.jsx').then(({ default: App }) => {
    root.render(
      <StrictMode>
        <App />
      </StrictMode>,
    )
  })
} else {
  root.render(<MissingKeysNotice />)
}
