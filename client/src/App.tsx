import { useEffect } from "react";
import { Routes, Route, useLocation, Navigate } from "react-router-dom";
import ChatComp from "./components/ChatComp";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import FlowViewer from "./pages/FlowViewer";
import Login from "./pages/SignIn";

const AppRoutes = [
  {
    path: "/login",
    element: <Login />,
    isPrivate: false,
  },
  {
    path: "/dashboard",
    element: <Dashboard />,
    isPrivate: true,
  },
  {
    path: "/chat/:chat_id",
    element: <ChatComp />,
    isPrivate: false,
  },
  {
    path: "/dashboard/:flow_id",
    element: <FlowViewer />,
    isPrivate: true,
  },
];

function App() {
  return (
    <>
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
      </Routes>
    </>
  );
}

export default App;
