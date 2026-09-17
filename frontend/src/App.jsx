import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import Home from "./pages/Home";
import Movies from "./pages/Movies";
import Recommendations from "./pages/Recommendations";
import MovieDetails from "./pages/MovieDetails";
import { AuthProvider } from "./context/AuthProvider";
import Register from "./pages/Register";
import Login from "./pages/Login";
import ProtectedRoute from "./components/ProtectedRoute";
import GuestRoute from "./components/GuestRoute";
import Profile from "./pages/Profile";
import AdminRoute from "./components/AdminRoute";
import AdminDashboard from "./pages/AdminDashboard";


function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>

          <Route element={<MainLayout />}>

            {/* Public routes */}
            <Route
              path="/"
              element={<Home />}
            />

            <Route
              path="/movies"
              element={<Movies />}
            />

            <Route
              path="/movies/:id"
              element={<MovieDetails />}
            />

            {/* Logged-out users only */}
            <Route element={<GuestRoute />}>

              <Route
                path="/login"
                element={<Login />}
              />

              <Route
                path="/register"
                element={<Register />}
              />

            </Route>


            {/* Logged-in users only */}
            <Route element={<ProtectedRoute />}>

              <Route
                path="/recommendations"
                element={<Recommendations />}
              />

              <Route
                path="/profile"
                element={<Profile />}
              />

            </Route>

            {/* Admin users only */}
            <Route element={<AdminRoute />}>

              <Route
                path="/admin"
                element={<AdminDashboard />}
              />

            </Route>

          </Route>

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;