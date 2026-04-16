import React from "react";
import ReactDOM from "react-dom/client";
import axios from "axios";
import "@/index.css";
import App from "@/App";

const apiUrl = (process.env.REACT_APP_API_URL || "http://localhost:8000").replace(/\/$/, "");

axios.defaults.baseURL = apiUrl;
axios.defaults.withCredentials = true;

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);