import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Resources from './pages/Resources';
import Hotspots from './pages/Hotspots';
import Predictions from './pages/Predictions';
import Admin from './pages/Admin';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/hotspots" element={<Hotspots />} />
          <Route path="/predictions" element={<Predictions />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;