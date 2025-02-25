// import logo from './logo.svg';
import './css/App.css'
import { useCallback, useState } from 'react';
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Cauldron from './pages/Cauldron.js'
import Game from './pages/Game.js'


// import Drag from './components/Drag'

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Cauldron/>}/>
        <Route path="/game" element={<Game/>}/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

