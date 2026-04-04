import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ComparePage from './pages/ComparePage'
import HomePage from './pages/HomePage'
import HistoryPage from './pages/HistoryPage'
import SimulationPage from './pages/SimulationPage'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="/simulation" element={<SimulationPage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
