import './styles.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { applyLargeTextOnBoot } from './largeText';

applyLargeTextOnBoot();

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
