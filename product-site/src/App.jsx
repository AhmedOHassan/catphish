import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Hero from './components/Hero'
import Documentation from './pages/Documentation'
import Team from './pages/Team'
import Privacy from './pages/Privacy'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Hero />} />
        <Route path="/documentation" element={<Documentation />} />
        <Route path="/team" element={<Team />} />
        <Route path="/privacy" element={<Privacy />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
