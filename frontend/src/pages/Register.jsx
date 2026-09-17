import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { register } from "../services/authService";


function Register() {
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] =
        useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");


    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");


        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }


        setLoading(true);

        try {
            await register(username, password);

            navigate("/login");
        } catch (error) {
            setError(
                error.response?.data?.message ||
                "Registration failed."
            );
        } finally {
            setLoading(false);
        }
    };


    return (
        <main className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl items-center justify-center px-4 py-12 sm:px-6 lg:px-8">

            <div className="w-full max-w-md">

                <div className="rounded-2xl border border-gray-800 bg-gray-900 p-6 shadow-xl sm:p-8">

                    <div className="mb-8 text-center">
                        <h1 className="text-3xl font-bold text-white">
                            Create Account
                        </h1>

                        <p className="mt-2 text-sm text-gray-400">
                            Create an account to start building
                            your movie profile.
                        </p>
                    </div>


                    {error && (
                        <div
                            role="alert"
                            className="mb-5 rounded-lg border border-red-900 bg-red-950/40 px-4 py-3 text-sm text-red-300"
                        >
                            {error}
                        </div>
                    )}


                    <form
                        onSubmit={handleSubmit}
                        className="space-y-5"
                    >

                        <div>
                            <label
                                htmlFor="username"
                                className="mb-2 block text-sm font-medium text-gray-300"
                            >
                                Username
                            </label>

                            <input
                                id="username"
                                type="text"
                                value={username}
                                onChange={(event) =>
                                    setUsername(event.target.value)
                                }
                                required
                                autoComplete="username"
                                className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30"
                            />
                        </div>


                        <div>
                            <label
                                htmlFor="password"
                                className="mb-2 block text-sm font-medium text-gray-300"
                            >
                                Password
                            </label>

                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(event) =>
                                    setPassword(event.target.value)
                                }
                                required
                                autoComplete="new-password"
                                className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30"
                            />
                        </div>


                        <div>
                            <label
                                htmlFor="confirmPassword"
                                className="mb-2 block text-sm font-medium text-gray-300"
                            >
                                Confirm Password
                            </label>

                            <input
                                id="confirmPassword"
                                type="password"
                                value={confirmPassword}
                                onChange={(event) =>
                                    setConfirmPassword(
                                        event.target.value
                                    )
                                }
                                required
                                autoComplete="new-password"
                                className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30"
                            />
                        </div>


                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full rounded-lg bg-red-600 px-4 py-3 font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                            {loading
                                ? "Creating account..."
                                : "Create Account"
                            }
                        </button>

                    </form>


                    <p className="mt-6 text-center text-sm text-gray-400">
                        Already have an account?{" "}

                        <Link
                            to="/login"
                            className="font-medium text-red-400 hover:text-red-300"
                        >
                            Login
                        </Link>
                    </p>

                </div>

            </div>

        </main>
    );
}

export default Register;