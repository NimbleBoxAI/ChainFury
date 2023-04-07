import "./App.css";
import { Routes, Route } from "react-router-dom";

function App() {
  const Home = () => {
    return <div>Home</div>;
  };

  const AboutUs = () => {
    return <div>AboutUs</div>;
  };

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about-us" element={<AboutUs />} />
    </Routes>
  );
}

export default App;
