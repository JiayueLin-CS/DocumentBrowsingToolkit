import React from 'react';
import DocumentsPage from './pages/DocumentsPage';
import SearchPage from './pages/SearchPage';
import DocumentPage from './pages/DocumentPage';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import BrowsePage from './pages/BrowsePage';

function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<HomePage />} />
        <Route exact path="/search" element={<SearchPage />} />
        <Route exact path="/browse" element={<BrowsePage />} />
        <Route exact path="/document/:documentId" element={<DocumentPage />} />
        <Route exact path="/documents/:topicId" element={<DocumentsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
