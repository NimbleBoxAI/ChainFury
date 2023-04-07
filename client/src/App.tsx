import { Routes, Route } from "react-router-dom";
import ChatComp from "./components/ChatComp";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/SignIn";
import SignUp from "./pages/SignUp";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/chat/:chat_id" element={<ChatComp />} />
    </Routes>
  );
}

export default App;
