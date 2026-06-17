import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import SlideDeck from './SlideDeck'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SlideDeck />
  </StrictMode>,
)
