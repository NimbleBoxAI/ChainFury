import { Alert, Snackbar } from '@mui/material';
import { useState } from 'react';
import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import ChatComp from './components/ChatComp';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import FlowViewer from './pages/FlowViewer';
import Login from './pages/SignIn';

const AppRoutes = [
  {
    path: '/ui/login',
    element: <Login />,
    isPrivate: false
  },
  {
    path: '/ui/dashboard',
    element: <Dashboard />,
    isPrivate: true
  },
  {
    path: '/ui/chat/:chat_id',
    element: <ChatComp />,
    isPrivate: false
  },
  {
    path: '/ui/dashboard/:flow_id',
    element: <FlowViewer />,
    isPrivate: true
  }
];

function App() {
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');

  window['alert'] = function (message: string) {
    setAlertMessage(message);
    setShowAlert(true);
  };

  return (
    <>
      <Snackbar
        open={showAlert}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        autoHideDuration={1000}
        onClose={() => {
          setShowAlert(false);
        }}
      >
        <Alert severity={'info'}>{alertMessage}</Alert>
      </Snackbar>{' '}
      <Routes>
        {AppRoutes.map((route, key) => (
          <Route
            key={key}
            path={route.path}
            element={
              route?.isPrivate ? (
                <div className="flex overflow-hidden">
                  <Sidebar />
                  {route.element}
                </div>
              ) : (
                route.element
              )
            }
          />
        ))}
        <Route path="*" element={<Navigate to="/ui/login" />} />
      </Routes>
    </>
  );
}

export default App;
