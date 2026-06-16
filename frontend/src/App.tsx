import { Routes, Route, Navigate } from 'react-router-dom'
import Chat from '@/pages/Chat'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Chat />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
