// import logo from './logo.svg';
import './css/App.css'
import { useCallback, useState } from 'react';
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import DropArea from './components/Drop.js';

import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import axios from 'axios';
import Card from './components/Card.js';
import CardList from './components/CardList.js';
import { debounce } from 'lodash';

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

