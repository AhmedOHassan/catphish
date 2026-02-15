import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Hero from './components/Hero'
import Documentation from './pages/Documentation'
import Team from './pages/Team'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Hero />} />
        <Route path="/documentation" element={<Documentation />} />
        <Route path="/team" element={<Team />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
