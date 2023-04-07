import { useAuthStates } from "./redux/hooks/dispatchHooks";
import { useAppDispatch } from "./redux/hooks/store";
import { setCount } from "./redux/slices/authSlice";
import "./App.css";

function App() {
  const { auth } = useAuthStates();
  const dispatch = useAppDispatch();

  const handleCount = () => {
    return dispatch(
      setCount({
        count: auth?.count + 1,
      })
    );
  };

  return (
    <div className="flex justify-center items-center h-full">
      <h1 onClick={handleCount} className="text-3xl font-bold underline">
        Chain Fury {auth?.count}
      </h1>
    </div>
  );
}

export default App;
