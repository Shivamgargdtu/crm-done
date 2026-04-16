import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import axios from "axios";

const API_URL = (process.env.REACT_APP_API_URL || "http://localhost:8000").replace(/\/$/, "");

// Safety net for every axios call in the app
axios.defaults.withCredentials = true;
axios.defaults.baseURL = API_URL;

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};

function formatApiErrorDetail(detail) {
    if (detail == null) return "Something went wrong. Please try again.";
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
        return detail
            .map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e)))
            .filter(Boolean)
            .join(" ");
    }
    if (detail && typeof detail.msg === "string") return detail.msg;
    return String(detail);
}

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const checkAuth = useCallback(async () => {
        try {
            const response = await axios.get(`${API_URL}/api/auth/me`, {
                withCredentials: true,
            });
            setUser(response.data);
            return true;
        } catch (err) {
            if (err.response?.status === 401) {
                try {
                    await axios.post(`${API_URL}/api/auth/refresh`, {}, { withCredentials: true });
                    const response = await axios.get(`${API_URL}/api/auth/me`, { withCredentials: true });
                    setUser(response.data);
                    return true;
                } catch {
                    setUser(null);
                    return false;
                }
            }
            setUser(null);
            return false;
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        checkAuth();

        const refreshInterval = setInterval(async () => {
            try {
                await axios.post(`${API_URL}/api/auth/refresh`, {}, { withCredentials: true });
            } catch {
                checkAuth();
            }
        }, 50 * 60 * 1000);

        return () => clearInterval(refreshInterval);
    }, [checkAuth]);

    const login = async (email, password) => {
        try {
            setError(null);
            const response = await axios.post(
                `${API_URL}/api/auth/login`,
                { email, password },
                { withCredentials: true }
            );
            setUser(response.data);
            return { success: true };
        } catch (err) {
            const errorMsg = formatApiErrorDetail(err.response?.data?.detail);
            setError(errorMsg);
            return { success: false, error: errorMsg };
        }
    };

    const logout = async () => {
        try {
            await axios.post(`${API_URL}/api/auth/logout`, {}, { withCredentials: true });
        } catch (err) {
            console.error("Logout error:", err);
        } finally {
            setUser(null);
        }
    };

    const refreshToken = async () => {
        try {
            await axios.post(`${API_URL}/api/auth/refresh`, {}, { withCredentials: true });
            await checkAuth();
            return true;
        } catch {
            setUser(null);
            return false;
        }
    };

    const value = {
        user,
        loading,
        error,
        login,
        logout,
        refreshToken,
        checkAuth,
        isAdmin: user?.role === "admin",
        isAuthenticated: !!user,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;