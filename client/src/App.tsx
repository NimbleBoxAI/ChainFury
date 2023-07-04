import { Alert, Snackbar } from '@mui/material';
import React from 'react';
import { ComponentType, lazy, Suspense, useState } from 'react';
import { Routes, Route, useLocation, Navigate } from 'react-router-dom';

function retry(fn: any, retriesLeft?: any, interval?: any) {
  if (!retriesLeft) retriesLeft = 10;
  if (!interval) interval = 1000;
  return new Promise((resolve, reject) => {
    fn()
      .then(resolve)
      .catch((error: any) => {
        setTimeout(() => {
          if (retriesLeft === 1) {
            // reject('maximum retries exceeded');
            reject(error);
            return;
          }
          // Passing on "reject" is the important part
          retry(fn, retriesLeft - 1, interval).then(resolve, reject);
        }, interval);
      });
  }) as Promise<{ default: ComponentType<any> }>;
}

const ChatComp = lazy(() => retry(() => import('./components/ChatComp')));
const Sidebar = lazy(() => retry(() => import('./components/Sidebar')));
const Dashboard = lazy(() => retry(() => import('./pages/Dashboard')));
const FlowViewer = lazy(() => retry(() => import('./pages/FlowViewer')));
const Login = lazy(() => retry(() => import('./pages/SignIn')));
const SignUp = lazy(() => retry(() => import('./pages/SignUp')));

const AppRoutes = [
  {
    path: '/ui/login',
    element: <Login />,
    isPrivate: false
  },
  {
    path: '/ui/signup',
    element: <SignUp />,
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

export const ChainFuryContext = React.createContext({
  engine: 'fury',
  setEngine: (engine: any) => {}
});

function App() {
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [engine, setEngine] = useState('fury');

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
      <Suspense fallback={<div>Loading...</div>}>
        <ChainFuryContext.Provider value={{ engine: engine, setEngine: setEngine }}>
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
        </ChainFuryContext.Provider>
      </Suspense>
    </>
  );
}

export default App;
