import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';

import App from './components/App';

ReactDOM.render(
  <React.StrictMode>
    <CssBaseline />
    <Container maxWidth="md" style={{ paddingTop: 24, paddingBottom: 24 }}>
      <Typography variant="h1" align="center" gutterBottom>
        Vending App!
      </Typography>

      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Container>
  </React.StrictMode>,
  document.getElementById('root')
);
